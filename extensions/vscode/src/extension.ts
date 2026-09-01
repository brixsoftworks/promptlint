import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('promptlint');
    const command = config.get<string>('path') || 'promptlint';

    // Specify the server options to execute the PromptLint language server
    const serverOptions: ServerOptions = {
        run: { command: command, args: ['lsp'] },
        debug: { command: command, args: ['lsp'] }
    };

    // Options to control the language client
    const clientOptions: LanguageClientOptions = {
        // Register the server for plain text and markdown documents
        documentSelector: [
            { scheme: 'file', language: 'plaintext' },
            { scheme: 'file', language: 'markdown' },
            { scheme: 'file', language: 'python' }
        ],
        synchronize: {
            // Notify the server about file changes to '.promptlintrc' files contained in the workspace
            fileEvents: vscode.workspace.createFileSystemWatcher('**/.promptlintrc')
        }
    };

    // Create the language client and start the client.
    client = new LanguageClient(
        'promptlint-ls',
        'PromptLint Language Server',
        serverOptions,
        clientOptions
    );

    // Start the client. This will also launch the server
    client.start();
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
