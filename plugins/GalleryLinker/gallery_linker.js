(function() {
    'use strict';

    const pluginId = 'gallery_linker';

    // Plugin configuration
    const config = {
        pluginId: pluginId,
        serverUrl: window.location.origin,

        // UI elements
        buttons: [
            {
                id: 'auto-link-scenes',
                text: 'Auto-Link Scenes',
                description: 'Automatically link galleries to related scenes',
                action: 'auto_link_scenes'
            },
            {
                id: 'auto-link-performers',
                text: 'Link Performers',
                description: 'Link performers to galleries based on file paths',
                action: 'auto_link_performers'
            },
            {
                id: 'generate-report',
                text: 'Generate Report',
                description: 'Generate linking statistics report',
                action: 'generate_report'
            }
        ]
    };

    // Create plugin UI
    function createPluginUI() {
        // Check if we're on a galleries page
        if (!window.location.pathname.includes('/galleries')) {
            return;
        }

        // Create plugin container
        const container = document.createElement('div');
        container.id = 'gallery-linker-plugin';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            z-index: 9999;
            min-width: 200px;
            color: white;
            font-family: Arial, sans-serif;
        `;

        // Create title
        const title = document.createElement('h4');
        title.textContent = 'Gallery Linker';
        title.style.cssText = 'margin: 0 0 10px 0; color: #fff;';
        container.appendChild(title);

        // Create buttons
        config.buttons.forEach(button => {
            const btn = document.createElement('button');
            btn.id = button.id;
            btn.textContent = button.text;
            btn.title = button.description;
            btn.style.cssText = `
                display: block;
                width: 100%;
                margin: 5px 0;
                padding: 8px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 3px;
                cursor: pointer;
                font-size: 12px;
            `;

            btn.addEventListener('mouseover', () => {
                btn.style.background = '#0056b3';
            });

            btn.addEventListener('mouseout', () => {
                btn.style.background = '#007bff';
            });

            btn.addEventListener('click', () => {
                executePluginAction(button.action, btn);
            });

            container.appendChild(btn);
        });

        // Create close button
        const closeBtn = document.createElement('button');
        closeBtn.textContent = '×';
        closeBtn.style.cssText = `
            position: absolute;
            top: 5px;
            right: 10px;
            background: none;
            border: none;
            color: #ccc;
            font-size: 16px;
            cursor: pointer;
            padding: 0;
            width: 20px;
            height: 20px;
        `;

        closeBtn.addEventListener('click', () => {
            container.remove();
        });

        container.appendChild(closeBtn);

        // Add minimize/restore functionality
        let minimized = false;
        title.style.cursor = 'pointer';
        title.addEventListener('click', () => {
            minimized = !minimized;
            const buttons = container.querySelectorAll('button:not(:last-child)');
            buttons.forEach(btn => {
                btn.style.display = minimized ? 'none' : 'block';
            });
            container.style.minWidth = minimized ? '120px' : '200px';
        });

        document.body.appendChild(container);
    }

    // Execute plugin action
    async function executePluginAction(action, buttonElement) {
        const originalText = buttonElement.textContent;

        try {
            // Update button state
            buttonElement.textContent = 'Running...';
            buttonElement.disabled = true;
            buttonElement.style.background = '#6c757d';

            // Call Stash GraphQL API to execute plugin
            const response = await fetch(`${config.serverUrl}/graphql`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: `
                        mutation RunPluginTask($plugin_id: ID!, $task_name: String!, $args: [PluginArgInput!]) {
                            runPluginTask(plugin_id: $plugin_id, task_name: $task_name, args: $args)
                        }
                    `,
                    variables: {
                        plugin_id: config.pluginId,
                        task_name: getTaskNameForAction(action),
                        args: [
                            {
                                key: 'mode',
                                value: action
                            }
                        ]
                    }
                })
            });

            const result = await response.json();

            if (result.errors) {
                throw new Error(result.errors.map(e => e.message).join(', '));
            }

            // Show success message
            showNotification(`${originalText} completed successfully!`, 'success');

        } catch (error) {
            console.error('Plugin execution error:', error);
            showNotification(`Error: ${error.message}`, 'error');

        } finally {
            // Restore button state
            buttonElement.textContent = originalText;
            buttonElement.disabled = false;
            buttonElement.style.background = '#007bff';
        }
    }

    // Get task name for action
    function getTaskNameForAction(action) {
        const taskMap = {
            'auto_link_scenes': 'Auto-Link Galleries to Scenes',
            'auto_link_performers': 'Auto-Link Performers to Galleries',
            'generate_report': 'Generate Linking Report'
        };
        return taskMap[action] || action;
    }

    // Show notification
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: ${type === 'error' ? '#dc3545' : '#28a745'};
            color: white;
            padding: 15px 25px;
            border-radius: 5px;
            z-index: 10000;
            font-family: Arial, sans-serif;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 400px;
            text-align: center;
        `;

        notification.textContent = message;
        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);

        // Click to dismiss
        notification.addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }

    // Initialize plugin when page loads
    function init() {
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // Wait a bit for Stash UI to initialize
        setTimeout(() => {
            createPluginUI();
        }, 2000);
    }

    // Handle navigation changes (Stash is a SPA)
    let currentPath = window.location.pathname;
    const observer = new MutationObserver(() => {
        if (currentPath !== window.location.pathname) {
            currentPath = window.location.pathname;

            // Remove existing plugin UI
            const existing = document.getElementById('gallery-linker-plugin');
            if (existing) {
                existing.remove();
            }

            // Re-create if on galleries page
            if (currentPath.includes('/galleries')) {
                setTimeout(createPluginUI, 1000);
            }
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Start initialization
    init();

})();