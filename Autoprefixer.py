import sublime
import sublime_plugin
from os.path import dirname, realpath, join

try:
    # Python 2
    from node_bridge import node_bridge
except:
    from .node_bridge import node_bridge

# monkeypatch `Region` to be iterable
sublime.Region.totuple = lambda self: (self.a, self.b)
sublime.Region.__iter__ = lambda self: self.totuple().__iter__()

BIN_PATH = join(sublime.packages_path(),
                dirname(realpath(__file__)), 'autoprefixer.js')


class AutoprefixerCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        if not self.is_css() and not self.is_unsaved_buffer_without_syntax():
            return
        browsers = ','.join(self.get_setting('browsers'))
        has_selection = False
        for region in self.view.sel():
            if region.empty():
                continue
            has_selection = True
            self.prefix(region, browsers)
        if not has_selection:
            self.prefix(sublime.Region(0, self.view.size()), browsers)

    def prefix(self, region, browsers):
        try:
            if node_bridge(self.view.substr(region), BIN_PATH, [browsers]):
                self.view.replace(edit, region, prefixed)
        except Exception as e:
            sublime.error_message('Autoprefixer\n%s' % e)

    def is_unsaved_buffer_without_syntax(self):
        return self.view.file_name() is None and self.is_plaintext()

    def is_plaintext(self):
        return self.view.settings().get('syntax') == 'Packages/Text/Plain text.tmLanguage'

    def is_css(self):
        return self.view.settings().get('syntax') == 'Packages/CSS/CSS.tmLanguage'

    def get_setting(self, key):
        settings = self.view.settings().get('Autoprefixer')
        if settings is None:
            settings = sublime.load_settings('Autoprefixer.sublime-settings')
        return settings.get(key)
