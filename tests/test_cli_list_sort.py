from typer.testing import CliRunner

from src.main import app, auto_register_commands

runner = CliRunner()


def test_all_sort_by_tags():
    auto_register_commands()
    with runner.isolated_filesystem():
        r1 = runner.invoke(app, ["contact", "add", "Pavlo", "1234567890"])
        assert r1.exit_code == 0, f"Add Pavlo failed: {r1.stdout}"
        r2 = runner.invoke(app, ["contact", "add", "Anna", "9876543210"])
        assert r2.exit_code == 0, f"Add Anna failed: {r2.stdout}"
        r3 = runner.invoke(app, ["contact", "tag", "add", "Pavlo", "ml"])
        assert r3.exit_code == 0, f"Tag-add Pavlo ml failed: {r3.stdout}"
        r4 = runner.invoke(app, ["contact", "tag", "add", "Pavlo", "ai"])
        assert r4.exit_code == 0, f"Tag-add Pavlo ai failed: {r4.stdout}"
        r5 = runner.invoke(app, ["contact", "tag", "add", "Anna", "ai"])
        assert r5.exit_code == 0, f"Tag-add Anna ai failed: {r5.stdout}"

        # sort by tag_count: Pavlo (2 tags) has to be before Anna (1 tag)
        r = runner.invoke(app, ["contact", "list", "--sort-by", "tag_count"])
        assert r.exit_code == 0, f"Exit code: {r.exit_code}\nOutput: {r.stdout}"
        out = r.stdout
        # Verify both names appear
        assert "Pavlo" in out, f"Pavlo not found in output:\n{out}"
        assert "Anna" in out, f"Anna not found in output:\n{out}"
        assert out.index("Pavlo") < out.index("Anna")

        # sort by tag_name: minimal tag "ai" Anna -> Anna must be before Pavlo (minimal tag "ai" == "ai")
        r = runner.invoke(app, ["contact", "list", "--sort-by", "tag_name"])
        assert r.exit_code == 0, r.stdout
        out = r.stdout
        assert out.index("Anna") < out.index("Pavlo")

def test_all_group_filter_current_and_all():
    auto_register_commands()
    with runner.isolated_filesystem():
        # default personal
        runner.invoke(app, ["group", "add", "work"])
        runner.invoke(app, ["contact", "add", "Alice", "1234567890"])  # personal
        runner.invoke(app, ["group", "use", "work"])
        runner.invoke(app, ["contact", "add", "Bob", "9876543210"])    # work

        # default (current group = work)
        r = runner.invoke(app, ["contact", "list"])
        assert r.exit_code == 0, r.stdout
        out = r.stdout
        assert "Bob" in out
        assert "Alice" not in out

        # explicit personal
        r = runner.invoke(app, ["contact", "list", "--group", "personal"])
        out = r.stdout
        assert "Alice" in out
        assert "Bob" not in out

        # all groups
        r = runner.invoke(app, ["contact", "list", "--group", "all"])
        out = r.stdout
        assert "Alice" in out and "Bob" in out
        # Check for group names with folder emoji
        assert "personal" in out
        assert "work" in out
