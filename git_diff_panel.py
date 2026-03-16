import sublime
import sublime_plugin
import subprocess
import os


def git(args, cwd):
    try:
        result = subprocess.check_output(
            ["git"] + args,
            cwd=cwd,
            stderr=subprocess.STDOUT
        )
        return result.decode("utf-8")
    except Exception:
        return ""


class GitPanelCommand(sublime_plugin.WindowCommand):

    def run(self):
        folders = self.window.folders()

        if not folders:
            sublime.message_dialog("Open a project folder first.")
            return

        self.root = folders[0]

        self.window.set_layout({
            "cols": [0, 0.3, 1],
            "rows": [0, 1],
            "cells": [
                [0, 0, 1, 1],  # file list
                [1, 0, 2, 1]   # diff view
            ]
        })

        self.files = self.get_modified_files()

        self.create_file_list()
        self.create_diff_view()

    def get_modified_files(self):
        output = git(["status", "--porcelain"], self.root)

        files = []

        for line in output.splitlines():
            file = line[3:]
            files.append(file)

        return files

    def create_file_list(self):
        self.window.focus_group(0)

        view = self.window.new_file()
        view.set_name("Git Changes")
        view.set_scratch(True)

        content = ""

        for f in self.files:
            content += f + "\n"

        view.run_command("append", {"characters": content})

        view.settings().set("git_panel", True)

    def create_diff_view(self):
        self.window.focus_group(1)

        view = self.window.new_file()
        view.set_name("Diff")
        view.set_scratch(True)
        view.set_syntax_file("Packages/Diff/Diff.sublime-syntax")


class GitOpenDiffCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        if not self.view.settings().get("git_panel"):
            return

        sel = self.view.sel()[0]
        line = self.view.line(sel)

        file = self.view.substr(line).strip()

        window = self.view.window()
        root = window.folders()[0]

        diff = git(["diff", file], root)

        for v in window.views():
            if v.name() == "Diff":
                diff_view = v
                break
        else:
            return

        window.focus_view(diff_view)

        diff_view.run_command("select_all")
        diff_view.run_command("right_delete")

        diff_view.run_command("append", {
            "characters": diff
        })
        
class GitPanelCloseCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.set_layout({
            "cols": [0, 1],
            "rows": [0, 1],
            "cells": [[0, 0, 1, 1]]
        })