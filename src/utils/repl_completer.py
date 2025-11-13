"""
Custom REPL completer with context-aware autocomplete.

Fixes multi-level command parameter position bug where Click's completer
shows completions from wrong parameter level.

Reads autocomplete directly from Typer command structure:
- Extracts autocompletion callbacks from Typer/Click command definitions
- Correctly tracks parameter position for multi-level commands
- Provides ONLY relevant suggestions for that specific parameter
- Calls the exact same autocomplete functions as shell completion

Single source of truth: Typer command definitions with autocompletion=... arguments!
"""

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from typing import Iterable, List, Optional
import click
import re


class ContextAwareCompleter(Completer):
    """
    Parameter-aware completer that provides context-specific suggestions.
    
    Fixes Click's REPL completer bug where multi-level commands (e.g., "notes add")
    show completions from the wrong parameter position.
    
    Reads autocompletion callbacks directly from Typer/Click argument definitions,
    ensuring single source of truth while correctly tracking parameter positions.
    """
    
    def __init__(self, original_completer, click_ctx=None):
        """
        Initialize with the original click_repl completer.
        
        Args:
            original_completer: The original prompt_toolkit completer from click_repl
            click_ctx: Click context (to inspect command structure)
        """
        self.original_completer = original_completer
        self.click_ctx = click_ctx
    
    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        """
        Get completions with correct parameter position tracking.
        
        For commands/subcommands: delegates to original completer (with error handling)
        For parameters: extracts callback from Typer definition and calls it
        
        Args:
            document: Current document state
            complete_event: Completion event
            
        Yields:
            Completion objects for valid suggestions
        """
        text = document.text_before_cursor
        
        # Strip prompt prefix if present (e.g., "[personal] > ")
        # Prompts typically end with "> " and may contain brackets
        prompt_pattern = r'^\[[\w\-]+\]\s*>\s*'
        stripped_text = re.sub(prompt_pattern, '', text)
        
        # Check if prompt was actually stripped
        has_prompt = (stripped_text != text)
        
        # Create modified document without prompt for consistent processing
        if has_prompt:
            modified_doc = Document(stripped_text, cursor_position=len(stripped_text))
        else:
            modified_doc = document
        
        words = stripped_text.split()
        
        # Get the Click command structure
        if not self.click_ctx:
            return
        
        ctx = self.click_ctx
        command = ctx.command
        
        # If empty, show top-level commands
        if len(words) == 0:
            if isinstance(command, click.MultiCommand):
                for name in command.list_commands(ctx):
                    yield Completion(name, start_position=0)
            return
        
        # If typing first word (command), show matching command completions
        if len(words) == 1 and not stripped_text.endswith(' '):
            if isinstance(command, click.MultiCommand):
                partial_cmd = words[0].lower()
                for name in command.list_commands(ctx):
                    if name.lower().startswith(partial_cmd):
                        yield Completion(name, start_position=-len(words[0]))
            return
        
        # Track position in words array as we navigate command structure
        current_cmd = command
        
        # For multi-level commands like "notes add", navigate to the final command
        word_idx = 0
        while word_idx < len(words) and isinstance(current_cmd, click.MultiCommand):
            word = words[word_idx]
            subcommand = current_cmd.get_command(ctx, word)
            if subcommand:
                current_cmd = subcommand
                word_idx += 1
            else:
                # Can't resolve this word as a subcommand
                # If we're typing the last word, show subcommand completions
                if word_idx == len(words) - 1 and not stripped_text.endswith(' '):
                    # Show available subcommands from current_cmd
                    if isinstance(current_cmd, click.MultiCommand):
                        for name in current_cmd.list_commands(ctx):
                            if name.lower().startswith(word.lower()):
                                yield Completion(name, start_position=-len(word))
                return
        
        # After navigation, check if we're still at a MultiCommand level
        # If yes and text ends with space, show subcommands
        if isinstance(current_cmd, click.MultiCommand) and stripped_text.endswith(' '):
            # Show subcommands (e.g., "notes " should show add, edit, list, etc.)
            for name in current_cmd.list_commands(ctx):
                yield Completion(name, start_position=0)
            return
        
        # Calculate parameter index (0-based)
        # Use word_idx (not cmd_depth) as it tracks actual position after navigation
        # If we have "notes add Alice ", we have:
        # - words = ['notes', 'add', 'Alice']
        # - word_idx = 2 (stopped after processing 'notes' and 'add')
        # - stripped_text.endswith(' ') = True
        # - param_index = 3 - 2 = 1 (second parameter)
        if stripped_text.endswith(' '):
            param_index = len(words) - word_idx
        else:
            param_index = len(words) - word_idx - 1
        
        # If we're still typing command/subcommand or before first parameter
        if param_index < 0:
            # Show subcommand completions
            if self.original_completer:
                try:
                    yield from self.original_completer.get_completions(modified_doc, complete_event)
                except Exception:
                    pass
            return
        
        # Get the parameter at this position from the Click command
        params = [p for p in current_cmd.params if isinstance(p, click.Argument)]
        
        if param_index >= len(params):
            # Beyond defined parameters, no completion
            return
        
        param = params[param_index]
        
        # Extract autocompletion callback from parameter
        # Typer stores custom callbacks in _custom_shell_complete
        autocomplete_fn = None
        if hasattr(param, '_custom_shell_complete'):
            autocomplete_fn = param._custom_shell_complete
        elif hasattr(param, 'autocompletion') and param.autocompletion:
            autocomplete_fn = param.autocompletion
        
        if not autocomplete_fn:
            # No autocomplete defined for this parameter - show nothing
            return
        
        # Get current word being typed
        if stripped_text.endswith(' '):
            current_word = ''
        else:
            current_word = words[-1] if words else ''
        
        # Build context with previously entered parameters
        # Parameters start at word_idx position (after all command/subcommand words)
        ctx_params = {}
        for i, prev_param in enumerate(params[:param_index]):
            param_word_idx = word_idx + i
            if param_word_idx < len(words):
                ctx_params[prev_param.name] = words[param_word_idx]
        
        # Create a minimal Click context for the autocomplete callback
        fake_ctx = click.Context(current_cmd)
        fake_ctx.params = ctx_params
        
        # Call the autocomplete function
        # Signature: (ctx, args, incomplete) -> List[CompletionItem] or List[str]
        try:
            suggestions = autocomplete_fn(fake_ctx, [], current_word)
            if suggestions:
                for suggestion in suggestions:
                    # Handle both CompletionItem objects and strings
                    if hasattr(suggestion, 'value'):
                        # It's a CompletionItem
                        text = suggestion.value
                    elif isinstance(suggestion, str):
                        text = suggestion
                    else:
                        continue
                    
                    # Filter by current word
                    if text.lower().startswith(current_word.lower()):
                        yield Completion(text, start_position=-len(current_word))
        except Exception as e:
            # If autocomplete fails, don't show anything
            pass


def create_context_aware_completer(click_completer, click_ctx=None):
    """
    Create a context-aware completer wrapper.
    
    Args:
        click_completer: The original Click completer
        click_ctx: Click context (to inspect command structure)
        
    Returns:
        ContextAwareCompleter instance
    """
    return ContextAwareCompleter(click_completer, click_ctx)


def create_context_aware_completer_for_repl(click_ctx):
    """
    Create a context-aware completer for REPL mode.
    
    This function properly instantiates the ClickCompleter and wraps it
    with our ContextAwareCompleter for correct parameter positioning.
    
    Args:
        click_ctx: Click context (to inspect command structure)
        
    Returns:
        ContextAwareCompleter instance ready for use with click_repl
    """
    try:
        from click_repl._completer import ClickCompleter
        # ClickCompleter expects (cli, ctx_args) where cli is the command
        # and ctx_args is a dictionary of context arguments
        click_completer = ClickCompleter(click_ctx.command, {})
        return ContextAwareCompleter(click_completer, click_ctx)
    except Exception:
        # If ClickCompleter instantiation fails, use a minimal completer
        # that only does our custom completion
        return ContextAwareCompleter(None, click_ctx)

