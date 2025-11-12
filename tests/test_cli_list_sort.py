from typer.testing import CliRunner

from src.main import app, auto_register_commands

runner = CliRunner()


def test_all_sort_by_tags():
    auto_register_commands()
    with runner.isolated_filesystem():
        runner.invoke(app, ["add", "Pavlo", "1234567890"])
        runner.invoke(app, ["add", "Anna", "1111111111"])
        runner.invoke(app, ["tag-add", "Pavlo", "ml"])
        runner.invoke(app, ["tag-add", "Pavlo", "ai"])
        runner.invoke(app, ["tag-add", "Anna", "ai"])

        # sort by tag_count: Pavlo (2 tags) has to be before Anna (1 tag)
        r = runner.invoke(app, ["all", "--sort-by", "tag_count"])
        assert r.exit_code == 0, r.stdout
        out = r.stdout
        assert out.index("Pavlo") < out.index("Anna")

        # sort by tag_name: minimal tag "ai" Anna -> Anna must be before Pavlo (minimal tag "ai" == "ai")
        r = runner.invoke(app, ["all", "--sort-by", "tag_name"])
        assert r.exit_code == 0, r.stdout
        out = r.stdout
        assert out.index("Anna") < out.index("Pavlo")

def test_all_group_filter_current_and_all():
    auto_register_commands()
    with runner.isolated_filesystem():
        # default personal
        runner.invoke(app, ["group-add", "work"])
        runner.invoke(app, ["add", "Alice", "1111111111"])  # personal
        runner.invoke(app, ["group-use", "work"])
        runner.invoke(app, ["add", "Bob", "2222222222"])    # work

        # default (current group = work)
        r = runner.invoke(app, ["all"])
        assert r.exit_code == 0, r.stdout
        out = r.stdout
        assert "Bob" in out
        assert "Alice" not in out

        # explicit personal
        r = runner.invoke(app, ["all", "--group", "personal"])
        out = r.stdout
        assert "Alice" in out
        assert "Bob" not in out

        # all groups
        r = runner.invoke(app, ["all", "--group", "all"])
        out = r.stdout
        assert "Alice" in out and "Bob" in out
        assert "Group: personal" in out
        assert "Group: work" in out
