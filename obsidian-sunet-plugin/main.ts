import { App, Editor, MarkdownView, Modal, Notice, Plugin, PluginSettingTab, Setting } from 'obsidian';

import { simpleGit, SimpleGit, CleanOptions } from 'simple-git';

// Remember to rename these classes and interfaces!

interface SunetPluginSettings {
  refreshURL: string;
  refreshUsername: string;
  refreshPassword: string;
}

const DEFAULT_SETTINGS: SunetPluginSettings = {
  refreshURL: 'https://staging.sunet.se/refresh-content',
  refreshUsername: 'editor',
  refreshPassword: 'dummy',
}

export default class SunetPlugin extends Plugin {
  settings: SunetPluginSettings;
  git: SimpleGit;

  async onload() {
    await this.loadSettings();

    const gitOptions: Partial<SimpleGitOptions> = {
      baseDir: this.app.vault.adapter.basePath,
      binary: 'git',
      maxConcurrentProcesses: 6,
      trimmed: false,
    };
    this.git = simpleGit(gitOptions);

    this.addCommand({
      id: 'discard-changes',
      name: 'Discard changes in current file',
      editorCallback: (editor: Editor, view: MarkdownView) => {
        this.discardChanges(view);
      },
    });
    this.addCommand({
      id: 'discard-all-changes',
      name: 'Discard changes in all files',
      callback: () => {
        this.discardAllChanges();
      },
    });
    this.addCommand({
      id: 'commit-push-and-fetch',
      name: 'Push all changes to staging',
      callback: () => {
        this.commitPushAndFetch();
      },
    });
    this.addCommand({
      id: 'hard-reset-force-push-and-fetch',
      name: 'Undo last push of changes to staging',
      callback: () => {
        this.hardResetForcePushAndFetch();
      },
    });

    // This adds a settings tab so the user can configure various aspects of the plugin
    this.addSettingTab(new SunetSettingTab(this.app, this));

    // If the plugin hooks up any global DOM events (on parts of the app that doesn't belong to this plugin)
    // Using this function will automatically remove the event listener when this plugin is disabled.
    this.registerDomEvent(document, 'click', (evt: MouseEvent) => {
      console.log('click', evt);
    });

    // When registering intervals, this function will automatically clear the interval when the plugin is disabled.
    this.registerInterval(window.setInterval(() => console.log('setInterval'), 5 * 60 * 1000));
  }

  onunload() {

  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }

  async discardChanges(view: MarkdownView) {
    const file = view.file;
    if (file) {
      const filePath = file.path;
      try {
        await this.git.checkout(['--', filePath]);
        new Notice('Unstaged changes discarded');
      } catch (error) {
        console.error('Error discarding changes:', error);
        new Notice('Failed to discard changes');
      }
    } else {
      new Notice('No file is currently active');
    }
  }
  async discardAllChanges() {
    try {
      // Discard all unstaged changes in the repository
      await this.git.checkout(['--', '.']);
      new Notice('All unstaged changes discarded');
    } catch (error) {
      console.error('Error discarding changes:', error);
      new Notice('Failed to discard all unstaged changes');
    }
  }
  async commitPushAndFetch() {
    try {
      // Stage, commit, and push changes
      await this.git.add('./*').commit('Auto-commit').push();

      const headers = new Headers();
      headers.append("Accept", "text/plain");
	  const credentials = btoa(`${this.settings.refreshUsername}:${this.settings.refreshPassword}`);
	  headers.append("Authorization", `Basic ${credentials}`);
      
      const fetchOptions = {
        method: 'get',
        mode: 'no-cors',
        headers: headers,
      };
      // Fetch data from example.com
      const response = await fetch(this.settings.refreshURL, fetchOptions);
      const body = await response.text();

      // Show the response in a Notice
      new Notice(body);
    } catch (error) {
      console.error('Error during operation:', error);
      new Notice('Operation failed');
    }
  }
  async hardResetForcePushAndFetch() {
    try {
      // Hard reset and force push
      await this.git.reset(['--hard', 'HEAD~1']);
      await this.git.push(['-f']);

      const headers = new Headers();
      headers.append("Accept", "text/plain");
	  const credentials = btoa(`${this.settings.refreshUsername}:${this.settings.refreshPassword}`);
	  headers.append("Authorization", `Basic ${credentials}`);
      
      const fetchOptions = {
        method: 'get',
        mode: 'no-cors',
        headers: headers,
      };

      // Fetch data from example.com
      const response = await fetch(this.settings.refreshURL, fetchOptions);
      const body = await response.text();

      // Show the response in a Notice
      new Notice(body);
    } catch (error) {
      console.error('Error during operation:', error);
      new Notice('Operation failed: ' + error.message);
    }
  }
}


class SunetSettingTab extends PluginSettingTab {
  plugin: SunetPlugin;

  constructor(app: App, plugin: SunetPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const {containerEl} = this;

    containerEl.empty();

    new Setting(containerEl)
      .setName('Staging URL')
      .setDesc('URL of the staging site for sunet.se, ending in /refresh-content')
      .addText(text => text
        .setPlaceholder('https://staging.sunet.se/refresh-content')
        .setValue(this.plugin.settings.refreshURL)
        .onChange(async (value) => {
          this.plugin.settings.refreshURL = value;
          await this.plugin.saveSettings();
        }));

    new Setting(containerEl)
      .setName('Staging Username')
      .setDesc('Basic auth username for the /refresh-content endpoint')
      .addText(text => text
        .setPlaceholder('editor')
        .setValue(this.plugin.settings.refreshUsername)
        .onChange(async (value) => {
          this.plugin.settings.refreshUsername = value;
          await this.plugin.saveSettings();
        }));

    new Setting(containerEl)
      .setName('Staging password')
      .setDesc('Basic auth password for the /refresh-content endpoint')
      .addText(text => text
        .setPlaceholder('dummy')
        .setValue(this.plugin.settings.refreshPassword)
        .onChange(async (value) => {
          this.plugin.settings.refreshPassword = value;
          await this.plugin.saveSettings();
        }));
  }
}
