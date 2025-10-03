#!/usr/bin/env python3
"""
MacSnap2HTML Enhanced - Clean Version with Anna's Fixes
Creates interactive HTML directory listings with collapsible folders
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime
import webbrowser

def format_size(size_bytes, decimal_places=1):
    """Convert bytes to human readable format with configurable decimal places"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.{decimal_places}f} {size_names[i]}"

def get_file_icon_class(file_path, is_dir=False):
    """Get CSS class for file icon based on extension"""
    if is_dir:
        return "folder"
    
    ext = os.path.splitext(file_path)[1].lower()
    
    icon_map = {
        '.pdf': 'pdf', '.doc': 'word', '.docx': 'word', '.txt': 'text',
        '.rtf': 'text', '.odt': 'text', '.pages': 'text',
        '.xls': 'excel', '.xlsx': 'excel', '.csv': 'excel', '.numbers': 'excel',
        '.ppt': 'powerpoint', '.pptx': 'powerpoint', '.key': 'powerpoint',
        '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image',
        '.bmp': 'image', '.tiff': 'image', '.svg': 'image', '.ico': 'image',
        '.webp': 'image', '.heic': 'image',
        '.mp4': 'video', '.avi': 'video', '.mov': 'video', '.mkv': 'video',
        '.wmv': 'video', '.flv': 'video', '.webm': 'video', '.m4v': 'video',
        '.mp3': 'audio', '.wav': 'audio', '.m4a': 'audio', '.flac': 'audio',
        '.aac': 'audio', '.ogg': 'audio', '.wma': 'audio',
        '.zip': 'archive', '.rar': 'archive', '.7z': 'archive', '.tar': 'archive',
        '.gz': 'archive', '.bz2': 'archive', '.dmg': 'archive',
        '.py': 'code', '.js': 'code', '.html': 'code', '.css': 'code',
        '.php': 'code', '.java': 'code', '.cpp': 'code', '.c': 'code',
        '.swift': 'code', '.go': 'code', '.rb': 'code', '.json': 'code',
        '.exe': 'executable', '.app': 'executable', '.deb': 'executable',
        '.rpm': 'executable', '.msi': 'executable',
    }
    
    return icon_map.get(ext, 'file')

class DirectoryScanner:
    def __init__(self):
        self.total_files = 0
        self.total_folders = 0
        self.total_size = 0
        self.items = []
        self.scan_time = ""
        
    def calculate_folder_size(self, folder_path):
        """Calculate total size of all files in a folder recursively"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        if not file.startswith('~') and not file.startswith('$'):
                            total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        continue
        except (OSError, IOError):
            pass
        return total_size
        
    def scan_directory(self, root_path, include_hidden=False, progress_callback=None):
        """Scan directory and collect all file/folder information"""
        self.total_files = 0
        self.total_folders = 0
        self.total_size = 0
        self.items = []
        self.scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Count items for progress - exclude hidden and temporary files
        total_items = 0
        for root, dirs, files in os.walk(root_path):
            if not include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.') and not f.startswith('~') and not f.startswith('$')]
            total_items += len(dirs) + len(files)
        
        processed = 0
        item_id = 0
        
        # Build hierarchical structure
        def process_directory(current_path, parent_id=None, level=0):
            nonlocal processed, item_id
            
            try:
                items = os.listdir(current_path)
                if not include_hidden:
                    items = [item for item in items if not item.startswith('.') 
                            and not item.startswith('~') 
                            and not item.startswith('$')]
                
                dirs = []
                files = []
                for item in items:
                    item_path = os.path.join(current_path, item)
                    try:
                        if os.path.isdir(item_path):
                            dirs.append(item)
                        elif os.path.isfile(item_path):
                            files.append(item)
                    except (OSError, IOError):
                        continue
                
                dirs.sort(key=str.lower)
                files.sort(key=str.lower)
                
                # Process directories
                for dir_name in dirs:
                    dir_path = os.path.join(current_path, dir_name)
                    abs_path = os.path.abspath(dir_path)

                    try:
                        stat_info = os.stat(dir_path)
                        modified = datetime.fromtimestamp(stat_info.st_mtime)
                        folder_size = self.calculate_folder_size(dir_path)

                        folder_item = {
                            'id': f"dir_{item_id}",
                            'name': dir_name,
                            'path': abs_path,
                            'full_path': dir_path,
                            'size_bytes': folder_size,
                            'size_formatted': format_size(folder_size),
                            'modified': modified.strftime('%Y-%m-%d %H:%M:%S'),
                            'is_dir': True,
                            'level': level,
                            'parent_id': parent_id,
                            'children': [],
                            'extension': '',
                            'icon_class': 'folder'
                        }
                        
                        current_id = folder_item['id']
                        self.items.append(folder_item)
                        item_id += 1
                        self.total_folders += 1
                        
                        processed += 1
                        if progress_callback:
                            progress_callback(processed, total_items)
                        
                        process_directory(dir_path, current_id, level + 1)
                        
                    except (OSError, IOError):
                        pass
                
                # Process files
                for file_name in files:
                    file_path = os.path.join(current_path, file_name)
                    abs_path = os.path.abspath(file_path)

                    try:
                        stat_info = os.stat(file_path)
                        file_size = stat_info.st_size
                        modified = datetime.fromtimestamp(stat_info.st_mtime)
                        extension = os.path.splitext(file_name)[1].lower()

                        file_item = {
                            'id': f"file_{item_id}",
                            'name': file_name,
                            'path': abs_path,
                            'full_path': file_path,
                            'size_bytes': file_size,
                            'size_formatted': format_size(file_size),
                            'modified': modified.strftime('%Y-%m-%d %H:%M:%S'),
                            'is_dir': False,
                            'level': level,
                            'parent_id': parent_id,
                            'children': [],
                            'extension': extension,
                            'icon_class': get_file_icon_class(file_path)
                        }
                        
                        self.items.append(file_item)
                        item_id += 1
                        self.total_files += 1
                        self.total_size += file_size
                        
                        processed += 1
                        if progress_callback:
                            progress_callback(processed, total_items)
                            
                    except (OSError, IOError):
                        pass
                        
            except (OSError, IOError):
                pass
        
        process_directory(root_path)
        
        # Build parent-child relationships
        item_map = {item['id']: item for item in self.items}
        for item in self.items:
            if item['parent_id'] and item['parent_id'] in item_map:
                parent = item_map[item['parent_id']]
                parent['children'].append(item['id'])

def generate_enhanced_html(scanner, root_path, output_file, title=None):
    """Generate HTML with file explorer-style interface"""

    root_name = title or os.path.basename(root_path.rstrip('/\\'))
    if not root_name:
        root_name = root_path

    js_data = []
    for item in scanner.items:
        js_data.append({
            'id': item['id'],
            'name': item['name'],
            'path': item['path'],
            'size': item['size_formatted'],
            'size_bytes': item['size_bytes'],
            'modified': item['modified'],
            'is_dir': item['is_dir'],
            'level': item['level'],
            'parent_id': item['parent_id'],
            'children': item['children'],
            'extension': item['extension'],
            'icon_class': item['icon_class']
        })

    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{root_name} - File Explorer</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #2c3e50;
            line-height: 1.4;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
            margin-top: 20px;
            margin-bottom: 20px;
            min-height: 90vh;
            display: flex;
            flex-direction: column;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            flex-shrink: 0;
        }}

        .header h1 {{
            font-size: 24px;
            margin-bottom: 8px;
            font-weight: 300;
        }}

        .header h1::before {{
            content: "📁";
            margin-right: 12px;
            font-size: 28px;
        }}

        .header .subtitle {{
            opacity: 0.9;
            font-size: 14px;
            margin-bottom: 15px;
            font-weight: 300;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
        }}

        .stat {{
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 12px;
            border-radius: 6px;
        }}

        .stat-number {{
            font-size: 18px;
            font-weight: bold;
            display: block;
        }}

        .stat-label {{
            font-size: 11px;
            opacity: 0.9;
            margin-top: 2px;
        }}

        .explorer-container {{
            display: flex;
            flex: 1;
            min-height: 0;
        }}

        .nav-pane {{
            width: 320px;
            background: #f8fafc;
            border-right: 1px solid #e1e8ed;
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }}

        .nav-header {{
            padding: 15px 20px;
            background: white;
            border-bottom: 1px solid #e1e8ed;
            font-weight: 600;
            font-size: 14px;
            color: #2c3e50;
        }}

        .nav-tree {{
            flex: 1;
            overflow-y: auto;
            padding: 10px 0;
        }}

        .nav-item {{
            display: flex;
            align-items: center;
            padding: 6px 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 13px;
        }}

        .nav-item:hover {{
            background: rgba(102, 126, 234, 0.1);
        }}

        .nav-item.selected {{
            background: #667eea;
            color: white;
        }}

        .nav-item.selected:hover {{
            background: #5a67d8;
        }}

        .nav-indent {{
            display: flex;
            align-items: center;
            min-width: 0;
            flex: 1;
        }}

        .nav-toggle {{
            width: 16px;
            height: 16px;
            margin-right: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            color: #667eea;
            border-radius: 3px;
            transition: all 0.2s ease;
            user-select: none;
        }}

        .nav-toggle:hover {{
            background: #f0f3ff;
            color: #4c63d2;
        }}

        .nav-toggle.expanded::before {{
            content: "▼";
        }}

        .nav-toggle.collapsed::before {{
            content: "▶";
        }}

        .nav-icon {{
            width: 18px;
            height: 16px;
            margin-right: 8px;
            background-size: 16px;
            background-repeat: no-repeat;
            background-position: center;
            flex-shrink: 0;
        }}

        .nav-name {{
            flex: 1;
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
        }}

        .breadcrumb-bar {{
            background: white;
            border-bottom: 1px solid #e1e8ed;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
        }}

        .breadcrumb-path {{
            background: #f8fafc;
            border: 1px solid #e1e8ed;
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 13px;
            color: #4a5568;
            flex: 1;
            font-family: 'Consolas', 'Monaco', monospace;
            cursor: text;
            user-select: text;
        }}

        .breadcrumb-copy {{
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s ease;
        }}

        .breadcrumb-copy:hover {{
            background: #5a67d8;
        }}

        .content-area {{
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 0;
        }}

        .content-header {{
            background: white;
            border-bottom: 1px solid #e1e8ed;
            padding: 15px 20px;
            flex-shrink: 0;
        }}

        .folder-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .folder-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 15px;
        }}

        .folder-stat {{
            text-align: center;
        }}

        .folder-stat-number {{
            font-size: 16px;
            font-weight: bold;
            color: #667eea;
            display: block;
        }}

        .folder-stat-label {{
            font-size: 11px;
            color: #6b7280;
            margin-top: 2px;
        }}

        .file-list {{
            flex: 1;
            overflow-y: auto;
            background: white;
        }}

        .file-item {{
            display: flex;
            align-items: center;
            padding: 10px 20px;
            border-bottom: 1px solid #f1f3f4;
            transition: all 0.2s ease;
            cursor: pointer;
        }}

        .file-item:hover {{
            background: #f8fafc;
        }}

        .file-item.folder {{
            cursor: pointer;
        }}

        .file-item.folder:hover {{
            background: rgba(102, 126, 234, 0.05);
        }}

        .file-icon {{
            width: 20px;
            height: 18px;
            margin-right: 12px;
            background-size: 18px;
            background-repeat: no-repeat;
            background-position: center;
            flex-shrink: 0;
        }}

        .file-name {{
            flex: 1;
            min-width: 0;
            font-size: 14px;
            color: #2c3e50;
            font-weight: 500;
        }}

        .file-name.folder {{
            color: #667eea;
            font-weight: 600;
        }}

        .file-details {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-left: auto;
            font-size: 12px;
            color: #6b7280;
        }}

        .file-size {{
            min-width: 80px;
            text-align: right;
        }}

        .file-date {{
            min-width: 130px;
        }}

        .file-ext {{
            min-width: 40px;
            text-align: center;
            font-size: 10px;
            text-transform: uppercase;
            font-weight: bold;
            color: #9ca3af;
        }}

        .controls {{
            background: white;
            padding: 15px 20px;
            border-bottom: 1px solid #e1e8ed;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
            flex-shrink: 0;
        }}

        .search-container {{
            flex: 1;
            min-width: 250px;
            position: relative;
        }}

        .search-box {{
            width: 100%;
            padding: 10px 35px 10px 14px;
            border: 2px solid #e1e8ed;
            border-radius: 6px;
            font-size: 13px;
            transition: all 0.3s ease;
        }}

        .search-box:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        .search-clear {{
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: #e1e8ed;
            border: none;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            cursor: pointer;
            color: #666;
            font-size: 12px;
            display: none;
            align-items: center;
            justify-content: center;
        }}

        .controls-group {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .expand-nav-btn {{
            padding: 8px 14px;
            border: 2px solid #28a745;
            background: #28a745;
            color: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .expand-nav-btn:hover {{
            background: #218838;
        }}

        .filters {{
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            padding: 6px 12px;
            border: 2px solid #e1e8ed;
            background: white;
            color: #666;
            border-radius: 15px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .filter-btn:hover {{
            background: #f8f9fa;
        }}

        .filter-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}

        .footer {{
            background: #f8fafc;
            padding: 15px 30px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
            border-top: 1px solid #e1e8ed;
            flex-shrink: 0;
        }}

        .footer strong {{
            color: #667eea;
        }}

        /* Icon styles */
        .icon-folder {{ background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="%23FFB347" viewBox="0 0 24 24"><path d="M9 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>'); }}
        .icon-file {{ background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="%23666666" viewBox="0 0 24 24"><path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/></svg>'); }}
        .icon-image {{ background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="%234F46E5" viewBox="0 0 24 24"><path d="M8.5,13.5L11,16.5L14.5,12L19,18H5M21,19V5C21,3.89 20.1,3 19,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19Z"/></svg>'); }}
        .icon-video {{ background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="%23EF4444" viewBox="0 0 24 24"><path d="M17,10.5V7A1,1 0 0,0 16,6H4A1,1 0 0,0 3,7V17A1,1 0 0,0 4,18H16A1,1 0 0,0 17,17V13.5L21,17.5V6.5L17,10.5Z"/></svg>'); }}
        .icon-audio {{ background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="%2310B981" viewBox="0 0 24 24"><path d="M14,3.23V5.29C16.89,6.15 19,8.83 19,12C19,15.17 16.89,17.84 14,18.7V20.77C18,19.86 21,16.28 21,12C21,7.72 18,4.14 14,3.23M16.5,12C16.5,10.23 15.5,8.71 14,7.97V16C15.5,15.29 16.5,13.76 16.5,12M3,9V15H7L12,20V4L7,9H3Z"/></svg>'); }}
        .icon-pdf {{ background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="%23DC2626" viewBox="0 0 24 24"><path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/></svg>'); }}
        .icon-code {{ background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="%230F72FF" viewBox="0 0 24 24"><path d="M9.4,16.6L4.8,12L9.4,7.4L8,6L2,12L8,18L9.4,16.6M14.6,16.6L19.2,12L14.6,7.4L16,6L22,12L16,18L14.6,16.6Z"/></svg>'); }}

        /* Indentation classes for nav tree */
        .nav-indent-1 {{ padding-left: 20px; }}
        .nav-indent-2 {{ padding-left: 40px; }}
        .nav-indent-3 {{ padding-left: 60px; }}
        .nav-indent-4 {{ padding-left: 80px; }}
        .nav-indent-5 {{ padding-left: 100px; }}
        .nav-indent-6 {{ padding-left: 120px; }}

        /* Responsive design */
        @media (max-width: 1200px) {{
            .nav-pane {{
                width: 280px;
            }}
        }}

        @media (max-width: 768px) {{
            .explorer-container {{
                flex-direction: column;
            }}

            .nav-pane {{
                width: 100%;
                height: 200px;
                border-right: none;
                border-bottom: 1px solid #e1e8ed;
            }}

            .nav-tree {{
                max-height: 180px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{root_name}</h1>
            <div class="subtitle">{root_path}</div>
            <div class="stats">
                <div class="stat">
                    <span class="stat-number">{scanner.total_files:,}</span>
                    <div class="stat-label">Files</div>
                </div>
                <div class="stat">
                    <span class="stat-number">{scanner.total_folders:,}</span>
                    <div class="stat-label">Folders</div>
                </div>
                <div class="stat">
                    <span class="stat-number">{format_size(scanner.total_size, 2)}</span>
                    <div class="stat-label">Total Size</div>
                </div>
                <div class="stat">
                    <span class="stat-number">{scanner.scan_time}</span>
                    <div class="stat-label">Generated</div>
                </div>
            </div>
        </div>

        <div class="explorer-container">
            <!-- Navigation Pane -->
            <div class="nav-pane">
                <div class="nav-header">📂 Directory Structure</div>
                <div class="nav-tree" id="navTree">
                </div>
            </div>

            <!-- Main Content Area -->
            <div class="main-content">
                <!-- Breadcrumb Bar -->
                <div class="breadcrumb-bar">
                    <span style="font-weight: 600; color: #4a5568; margin-right: 8px;">📍</span>
                    <div class="breadcrumb-path" id="breadcrumbPath">{root_path}</div>
                    <button class="breadcrumb-copy" id="copyPathBtn">Copy Path</button>
                </div>

                <!-- Controls -->
                <div class="controls">
                    <div class="search-container">
                        <input type="text" class="search-box" placeholder="Search current folder..." id="searchBox">
                        <button class="search-clear" id="searchClear">×</button>
                    </div>
                    <div class="controls-group">
                        <button class="expand-nav-btn" id="expandNavBtn">Expand Nav</button>
                        <div class="filters">
                            <button class="filter-btn active" data-filter="all">All</button>
                            <button class="filter-btn" data-filter="folders">Folders</button>
                            <button class="filter-btn" data-filter="files">Files</button>
                            <button class="filter-btn" data-filter="images">Images</button>
                            <button class="filter-btn" data-filter="documents">Documents</button>
                            <button class="filter-btn" data-filter="videos">Videos</button>
                            <button class="filter-btn" data-filter="audio">Audio</button>
                        </div>
                    </div>
                </div>

                <!-- Content Area -->
                <div class="content-area">
                    <div class="content-header">
                        <div class="folder-title" id="folderTitle">{root_name}</div>
                        <div class="folder-stats" id="folderStats">
                            <!-- Stats will be populated by JavaScript -->
                        </div>
                    </div>

                    <div class="file-list" id="fileList">
                        <!-- Files will be populated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            Generated by <strong>MacSnap2HTML Enhanced</strong> • {len(scanner.items):,} items processed •
            <strong>Features: File Explorer interface with navigation pane, breadcrumbs, and folder statistics</strong>
        </div>
    </div>

    <script>
        const fileData = {json.dumps(js_data, indent=2)};

        let currentFilter = 'all';
        let currentSearch = '';
        let expandedFolders = new Set();
        let currentFolderId = null;
        let allExpanded = false;

        // DOM elements
        const navTree = document.getElementById('navTree');
        const breadcrumbPath = document.getElementById('breadcrumbPath');
        const copyPathBtn = document.getElementById('copyPathBtn');
        const searchBox = document.getElementById('searchBox');
        const searchClear = document.getElementById('searchClear');
        const filterButtons = document.querySelectorAll('.filter-btn');
        const expandNavBtn = document.getElementById('expandNavBtn');
        const folderTitle = document.getElementById('folderTitle');
        const folderStats = document.getElementById('folderStats');
        const fileList = document.getElementById('fileList');

        function initExplorer() {{
            buildHierarchy();
            renderNavTree();

            // Find root folder
            const rootItem = fileData.find(item => !item.parent_id);
            if (rootItem) {{
                navigateToFolder(rootItem.id);
            }}

            setupEventListeners();
        }}

        function buildHierarchy() {{
            const itemMap = new Map();

            fileData.forEach(item => {{
                itemMap.set(item.id, {{...item, children: []}});
            }});

            fileData.forEach(item => {{
                if (item.parent_id && itemMap.has(item.parent_id)) {{
                    const parent = itemMap.get(item.parent_id);
                    parent.children.push(item.id);
                }}
            }});

            window.itemMap = itemMap;
        }}

        function renderNavTree() {{
            navTree.innerHTML = '';
            const rootItems = fileData.filter(item => !item.parent_id);

            rootItems.forEach(item => {{
                renderNavItem(item, 0);
            }});
        }}

        function renderNavItem(item, level) {{
            const element = createNavItemElement(item, level);
            navTree.appendChild(element);

            if (item.is_dir && expandedFolders.has(item.id)) {{
                const children = item.children || [];
                children.forEach(childId => {{
                    const childItem = window.itemMap.get(childId);
                    if (childItem) {{
                        renderNavItem(childItem, level + 1);
                    }}
                }});
            }}
        }}

        function createNavItemElement(item, level) {{
            const div = document.createElement('div');
            div.className = `nav-item ${{currentFolderId === item.id ? 'selected' : ''}}`;
            div.dataset.id = item.id;
            div.dataset.level = level;

            const hasChildren = item.is_dir && item.children && item.children.length > 0;
            const isExpanded = expandedFolders.has(item.id);
            const indentClass = level > 0 ? `nav-indent-${{Math.min(level, 6)}}` : '';

            let toggleIcon = '';
            if (hasChildren) {{
                toggleIcon = `<div class="nav-toggle ${{isExpanded ? 'expanded' : 'collapsed'}}" data-item-id="${{item.id}}"></div>`;
            }}

            div.innerHTML = `
                <div class="nav-indent ${{indentClass}}">
                    ${{toggleIcon}}
                    <div class="nav-icon icon-${{item.icon_class}}"></div>
                    <div class="nav-name">${{escapeHtml(item.name)}}</div>
                </div>
            `;

            return div;
        }}

        function navigateToFolder(folderId) {{
            currentFolderId = folderId;
            const folder = window.itemMap.get(folderId);

            if (folder) {{
                // Update breadcrumb
                breadcrumbPath.textContent = folder.path || folder.name;

                // Update folder title
                folderTitle.textContent = folder.name;

                // Update navigation selection
                document.querySelectorAll('.nav-item').forEach(item => {{
                    item.classList.remove('selected');
                }});
                const selectedNavItem = document.querySelector(`.nav-item[data-id="${{folderId}}"]`);
                if (selectedNavItem) {{
                    selectedNavItem.classList.add('selected');
                    selectedNavItem.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }}

                // Render folder contents
                renderFolderContents(folder);
                updateFolderStats(folder);
            }}
        }}

        function renderFolderContents(folder) {{
            fileList.innerHTML = '';

            if (!folder.children || folder.children.length === 0) {{
                fileList.innerHTML = '<div style="padding: 40px; text-align: center; color: #6b7280; font-style: italic;">This folder is empty</div>';
                return;
            }}

            folder.children.forEach(childId => {{
                const childItem = window.itemMap.get(childId);
                if (childItem && shouldShowItem(childItem)) {{
                    const element = createFileItemElement(childItem);
                    fileList.appendChild(element);
                }}
            }});
        }}

        function createFileItemElement(item) {{
            const div = document.createElement('div');
            div.className = `file-item ${{item.is_dir ? 'folder' : ''}}`;
            div.dataset.id = item.id;

            div.innerHTML = `
                <div class="file-icon icon-${{item.icon_class}}"></div>
                <div class="file-name ${{item.is_dir ? 'folder' : ''}}">${{escapeHtml(item.name)}}</div>
                <div class="file-details">
                    <div class="file-size">${{item.size}}</div>
                    <div class="file-date">${{item.modified}}</div>
                    <div class="file-ext">${{item.extension ? item.extension.substring(1).toUpperCase() : (item.is_dir ? 'DIR' : '')}}</div>
                </div>
            `;

            return div;
        }}

        function updateFolderStats(folder) {{
            const children = folder.children || [];
            const folders = children.filter(id => {{
                const item = window.itemMap.get(id);
                return item && item.is_dir;
            }});
            const files = children.filter(id => {{
                const item = window.itemMap.get(id);
                return item && !item.is_dir;
            }});
            const totalSize = children.reduce((sum, id) => {{
                const item = window.itemMap.get(id);
                return sum + (item ? item.size_bytes : 0);
            }}, 0);

            folderStats.innerHTML = `
                <div class="folder-stat">
                    <span class="folder-stat-number">${{folders.length}}</span>
                    <div class="folder-stat-label">Folders</div>
                </div>
                <div class="folder-stat">
                    <span class="folder-stat-number">${{files.length}}</span>
                    <div class="folder-stat-label">Files</div>
                </div>
                <div class="folder-stat">
                    <span class="folder-stat-number">${{formatSize(totalSize)}}</span>
                    <div class="folder-stat-label">Size</div>
                </div>
                <div class="folder-stat">
                    <span class="folder-stat-number">${{children.length}}</span>
                    <div class="folder-stat-label">Total Items</div>
                </div>
            `;
        }}

        function shouldShowItem(item) {{
            if (currentSearch) {{
                const searchLower = currentSearch.toLowerCase();
                if (!item.name.toLowerCase().includes(searchLower)) {{
                    return false;
                }}
            }}

            if (currentFilter === 'all') return true;
            if (currentFilter === 'folders') return item.is_dir;
            if (currentFilter === 'files') return !item.is_dir;

            if (!item.is_dir) {{
                const ext = item.extension.toLowerCase();
                switch (currentFilter) {{
                    case 'images':
                        return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', '.webp', '.heic', '.ico'].includes(ext);
                    case 'documents':
                        return ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages', '.xls', '.xlsx', '.csv', '.ppt', '.pptx'].includes(ext);
                    case 'videos':
                        return ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'].includes(ext);
                    case 'audio':
                        return ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma', '.mp2', '.aiff'].includes(ext);
                }}
            }}

            return false;
        }}

        function setupEventListeners() {{
            // Navigation tree events
            navTree.addEventListener('click', function(e) {{
                const navItem = e.target.closest('.nav-item');
                const toggle = e.target.closest('.nav-toggle');

                if (toggle) {{
                    const itemId = toggle.dataset.itemId;
                    if (expandedFolders.has(itemId)) {{
                        expandedFolders.delete(itemId);
                    }} else {{
                        expandedFolders.add(itemId);
                    }}
                    renderNavTree();
                }} else if (navItem) {{
                    const itemId = navItem.dataset.id;
                    const item = window.itemMap.get(itemId);
                    if (item && item.is_dir) {{
                        navigateToFolder(itemId);
                    }}
                }}
            }});

            // File list events
            fileList.addEventListener('click', function(e) {{
                const fileItem = e.target.closest('.file-item');
                if (fileItem && fileItem.classList.contains('folder')) {{
                    const itemId = fileItem.dataset.id;
                    navigateToFolder(itemId);
                }}
            }});

            // Search events
            searchBox.addEventListener('input', function() {{
                currentSearch = this.value;
                if (currentFolderId) {{
                    const folder = window.itemMap.get(currentFolderId);
                    if (folder) {{
                        renderFolderContents(folder);
                    }}
                }}
                searchClear.style.display = this.value ? 'flex' : 'none';
            }});

            searchClear.addEventListener('click', function() {{
                searchBox.value = '';
                currentSearch = '';
                if (currentFolderId) {{
                    const folder = window.itemMap.get(currentFolderId);
                    if (folder) {{
                        renderFolderContents(folder);
                    }}
                }}
                this.style.display = 'none';
                searchBox.focus();
            }});

            // Filter events
            filterButtons.forEach(btn => {{
                btn.addEventListener('click', function() {{
                    filterButtons.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    currentFilter = this.dataset.filter;
                    if (currentFolderId) {{
                        const folder = window.itemMap.get(currentFolderId);
                        if (folder) {{
                            renderFolderContents(folder);
                        }}
                    }}
                }});
            }});

            // Expand navigation
            expandNavBtn.addEventListener('click', function() {{
                if (allExpanded) {{
                    expandedFolders.clear();
                    this.textContent = 'Expand Nav';
                    allExpanded = false;
                }} else {{
                    fileData.forEach(item => {{
                        if (item.is_dir && item.children && item.children.length > 0) {{
                            expandedFolders.add(item.id);
                        }}
                    }});
                    this.textContent = 'Collapse Nav';
                    allExpanded = true;
                }}
                renderNavTree();
            }});

            // Copy path button
            copyPathBtn.addEventListener('click', function() {{
                navigator.clipboard.writeText(breadcrumbPath.textContent).then(function() {{
                    const originalText = copyPathBtn.textContent;
                    copyPathBtn.textContent = 'Copied!';
                    copyPathBtn.style.background = '#28a745';
                    setTimeout(() => {{
                        copyPathBtn.textContent = originalText;
                        copyPathBtn.style.background = '#667eea';
                    }}, 1500);
                }});
            }});

            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {{
                if ((e.ctrlKey || e.metaKey) && e.key === 'f') {{
                    e.preventDefault();
                    searchBox.focus();
                    searchBox.select();
                }}
            }});
        }}

        function formatSize(bytes) {{
            if (bytes === 0) return '0 B';
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(1024));
            return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + sizes[i];
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        document.addEventListener('DOMContentLoaded', initExplorer);
    </script>
</body>
</html>'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)

class MacSnap2HTMLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MacSnap2HTML Enhanced")
        # Make window full screen
        self.root.state('zoomed')
        self.root.attributes('-fullscreen', True)
        # Allow user to exit fullscreen with Escape key
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.minsize(1200, 800)
        self.root.resizable(True, True)
        
        self.setup_styles()
        
        self.scanner = DirectoryScanner()
        self.selected_directory = tk.StringVar()
        self.include_hidden = tk.BooleanVar(value=False)
        self.custom_title = tk.StringVar()
        
        self.create_widgets()
        
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), foreground='#7f8c8d')
        style.configure('Header.TLabel', font=('Segoe UI', 11, 'bold'), foreground='#34495e')
        style.configure('Modern.TButton', font=('Segoe UI', 10), padding=(15, 8))
        style.configure('Action.TButton', font=('Segoe UI', 11, 'bold'), padding=(20, 10))
        
        self.root.configure(bg='#f8fafc')
        
    def create_widgets(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        header_frame = tk.Frame(main_container, bg='#667eea', relief='flat')
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        header_content = tk.Frame(header_frame, bg='#667eea')
        header_content.pack(fill=tk.BOTH, padx=30, pady=25)
        
        title_label = tk.Label(header_content, text="MacSnap2HTML Enhanced", 
                              font=('Segoe UI', 22, 'bold'), 
                              fg='white', bg='#667eea')
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(header_content, 
                                 text="Create beautiful, interactive HTML directory listings with collapsible folders",
                                 font=('Segoe UI', 11), 
                                 fg='#e8eaff', bg='#667eea')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Directory selection section
        dir_section = ttk.LabelFrame(main_container, text="Select Directory", padding=20)
        dir_section.pack(fill=tk.X, pady=(0, 20))
        
        # Browse instructions
        browse_frame = tk.Frame(dir_section, bg='#f1f3f4', relief='solid', bd=1)
        browse_frame.pack(fill=tk.X, pady=(0, 15))
        
        browse_label = tk.Label(browse_frame, 
                               text="Click Browse below to select a folder",
                               font=('Segoe UI', 12, 'bold'), 
                               fg='#667eea', bg='#f1f3f4')
        browse_label.pack(pady=30)
        
        # Directory path and browse button
        path_frame = ttk.Frame(dir_section)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        path_label = ttk.Label(path_frame, text="Selected Directory:", font=('Segoe UI', 10, 'bold'))
        path_label.pack(anchor='w')
        
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.dir_entry = ttk.Entry(path_entry_frame, textvariable=self.selected_directory, 
                                  font=('Segoe UI', 10), state='readonly')
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(path_entry_frame, text="Browse...", 
                               style='Modern.TButton',
                               command=self.browse_directory)
        browse_btn.pack(side=tk.RIGHT)
        
        # Options section
        options_section = ttk.LabelFrame(main_container, text="Options", padding=20)
        options_section.pack(fill=tk.X, pady=(0, 20))
        
        options_grid = ttk.Frame(options_section)
        options_grid.pack(fill=tk.X)
        
        left_options = ttk.Frame(options_grid)
        left_options.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(left_options, text="Custom Title:", font=('Segoe UI', 10, 'bold'))
        title_label.pack(anchor='w')
        
        self.title_entry = ttk.Entry(left_options, textvariable=self.custom_title, 
                                    font=('Segoe UI', 10))
        self.title_entry.pack(fill=tk.X, pady=(5, 10))
        
        right_options = ttk.Frame(options_grid)
        right_options.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        hidden_cb = ttk.Checkbutton(right_options, 
                                   text="Include hidden files and folders",
                                   variable=self.include_hidden,
                                   style='TCheckbutton')
        hidden_cb.pack(anchor='w', pady=10)
        
        # Progress section
        progress_section = ttk.LabelFrame(main_container, text="Progress", padding=20)
        progress_section.pack(fill=tk.X, pady=(0, 20))
        
        self.progress = ttk.Progressbar(progress_section, mode='determinate', length=400)
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(progress_section, text="Ready to create directory listings...", 
                                     font=('Segoe UI', 10))
        self.status_label.pack()
        
        # Action buttons at bottom
        button_section = ttk.Frame(main_container)
        button_section.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        self.generate_btn = ttk.Button(button_section, text="GENERATE HTML LISTING", 
                                      style='Action.TButton',
                                      command=self.generate_html, state='disabled')
        self.generate_btn.pack(pady=10, fill=tk.X)
        
        secondary_buttons = ttk.Frame(button_section)
        secondary_buttons.pack(fill=tk.X)
        
        help_btn = ttk.Button(secondary_buttons, text="Help", 
                             style='Modern.TButton',
                             command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        about_btn = ttk.Button(secondary_buttons, text="About", 
                              style='Modern.TButton',
                              command=self.show_about)
        about_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        quit_btn = ttk.Button(secondary_buttons, text="Exit", 
                             style='Modern.TButton',
                             command=self.root.quit)
        quit_btn.pack(side=tk.RIGHT)
    
    def browse_directory(self):
        directory = filedialog.askdirectory(
            title="Select Directory to Scan",
            mustexist=True
        )
        if directory:
            self.selected_directory.set(directory)
            self.generate_btn.config(state='normal')
            self.status_label.config(text=f"Selected: {os.path.basename(directory)}")
    
    def update_progress(self, current, total):
        if total > 0:
            progress_percent = (current / total) * 100
            self.progress['value'] = progress_percent
            self.status_label.config(text=f"Processing... {current:,}/{total:,} items ({progress_percent:.1f}%)")
            self.root.update_idletasks()
    
    def generate_html(self):
        directory = self.selected_directory.get()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Error", "Please select a valid directory")
            return
        
        default_name = f"{os.path.basename(directory)}_enhanced_listing.html"
        output_file = filedialog.asksaveasfilename(
            title="Save Enhanced HTML file as...",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            initialfile=default_name
        )
        
        if not output_file:
            return
        
        self.generate_btn.config(state='disabled')
        self.progress['value'] = 0
        
        def scan_and_generate():
            try:
                self.status_label.config(text="Analyzing directory structure...")
                self.root.update_idletasks()
                
                self.scanner.scan_directory(
                    directory, 
                    self.include_hidden.get(), 
                    self.update_progress
                )
                
                self.status_label.config(text="Creating enhanced HTML with collapsible folders...")
                self.root.update_idletasks()
                
                title = self.custom_title.get().strip() if self.custom_title.get().strip() else None
                generate_enhanced_html(self.scanner, directory, output_file, title)
                
                self.progress['value'] = 100
                self.status_label.config(text="Enhanced HTML listing generated successfully!")
                
                result = messagebox.askyesno("Success!",
                    f"Enhanced HTML File Explorer created!\n\n"
                    f"Statistics:\n"
                    f"• Files: {self.scanner.total_files:,}\n"
                    f"• Folders: {self.scanner.total_folders:,}\n"
                    f"• Total Size: {format_size(self.scanner.total_size, 2)}\n\n"
                    f"New File Explorer Features:\n"
                    f"• Left navigation pane with directory tree\n"
                    f"• Breadcrumb navigation (copy paths easily)\n"
                    f"• Current folder highlighting & statistics\n"
                    f"• Click folders to navigate\n"
                    f"• Real-time search & filtering\n"
                    f"• Mobile responsive design\n\n"
                    f"File: {os.path.basename(output_file)}\n\n"
                    f"Open the HTML file now?")
                
                if result:
                    webbrowser.open(f"file://{os.path.abspath(output_file)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
                self.status_label.config(text="Error occurred during generation")
            finally:
                self.generate_btn.config(state='normal')
        
        thread = threading.Thread(target=scan_and_generate, daemon=True)
        thread.start()
    
    def show_help(self):
        help_text = """MacSnap2HTML Enhanced - File Explorer Interface - Help

HOW TO USE:
1. Click "Browse..." to select your directory
2. (Optional) Enter a custom title
3. (Optional) Check "Include hidden files" if needed
4. Click "GENERATE HTML LISTING"
5. Choose where to save your HTML file

NEW FILE EXPLORER FEATURES:
• Navigation Pane - Directory tree on the left with expand/collapse
• Breadcrumb Navigation - Shows current path, copy to clipboard
• Folder Statistics - Live metrics for current folder
• Click to Navigate - Click folders in nav pane or main area
• Current Folder Highlighting - See your location in the tree
• Expand All/Collapse All - Control navigation tree expansion

SEARCH & FILTERING:
• Real-time search within current folder
• File type filters - Images, Documents, Videos, Audio
• Search works with Ctrl+F keyboard shortcut

ADDITIONAL FEATURES:
• Mobile responsive design
• Professional modern interface
• Copy file paths easily
• Folder size calculations

REQUIREMENTS:
• Python 3.6 or later
• Works on Windows, Mac, and Linux

The generated HTML file can be opened in any web browser
and shared via email with no special software required."""
        
        messagebox.showinfo("Help", help_text)
    
    def show_about(self):
        about_text = """MacSnap2HTML Enhanced v2.0 - File Explorer Interface

A modern directory listing tool that creates interactive HTML files
with a professional file explorer interface.

New File Explorer Features:
• Left navigation pane with directory tree
• Breadcrumb navigation with copy-to-clipboard
• Current folder highlighting and statistics
• Click-to-navigate folder browsing
• Expandable/collapsible navigation tree
• Real-time folder metrics and content display

Additional Features:
• Advanced search and filtering
• Mobile responsive design
• Professional modern interface
• Easy file path copying

Built for NOAA data scientists and researchers.

Copyright © 2025"""

        messagebox.showinfo("About MacSnap2HTML Enhanced", about_text)

def main():
    root = tk.Tk()
    app = MacSnap2HTMLApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()