TEMPLATE_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background: #fff;
    color: #333;
}

h1, h2, h3, h4, h5, h6 {
    color: #000;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h1 {
    border-bottom: 2px solid #000;
    padding-bottom: 0.5rem;
}

a {
    color: #000;
    text-decoration: underline;
}

a:hover {
    background: #000;
    color: #fff;
}

code {
    background: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Monaco', 'Consolas', monospace;
}

pre {
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 5px;
    overflow-x: auto;
}

blockquote {
    border-left: 4px solid #000;
    margin-left: 0;
    padding-left: 1rem;
    font-style: italic;
}

.note-list {
    list-style: none;
    padding: 0;
}

.note-item {
    margin-bottom: 1rem;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 5px;
}

.note-title {
    font-weight: bold;
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
}

.note-date {
    font-size: 0.9rem;
    color: #666;
}

.back-link {
    margin-bottom: 2rem;
    display: inline-block;
}

.footer {
    margin-top: 4rem;
    padding-top: 2rem;
    border-top: 1px solid #ddd;
    text-align: center;
    color: #666;
    font-size: 0.9rem;
}
"""