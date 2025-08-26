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

/* Bigger search input that matches note-card width and style */
#search {
    display: block;
    width: 100%;
    box-sizing: border-box;       /* include padding in width */
    padding: 0.75rem 1rem;        /* taller input */
    font-size: 1.05rem;           /* larger font */
    line-height: 1.4;
    border: 1px solid #ddd;       /* match note border */
    border-radius: 5px;           /* same radius as cards */
    margin: 0 0 1rem 0;           /* space below */
    background: #fff;
    color: inherit;
}

/* focus state */
#search:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(0,0,0,0.06);
    border-color: #999;
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
/* Dark mode support using prefers-color-scheme */
@media (prefers-color-scheme: dark) {
    body {
        background: #222;
        color: #eee;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #fff;
    }
    h1 {
        border-bottom: 2px solid #fff;
    }
    a {
        color: #fff;
    }
    a:hover {
        background: #fff;
        color: #000;
    }
    code {
        background: #333;
        color: #fff;
    }
    pre {
        background: #333;
        color: #fff;
    }
    blockquote {
        border-left: 4px solid #fff;
    }
    .note-item {
        border: 1px solid #444;
        background: #2a2a2a;
    }
    .note-title {
        color: #fff;
    }
    .note-date {
        color: #aaa;
    }
    .footer {
        border-top: 1px solid #444;
        color: #aaa;
    }
    /* Dark mode variants for search input */
    #search {
        background: #2a2a2a;
        color: #eee;
        border: 1px solid #444;
    }

    #search:focus {
        box-shadow: 0 0 0 3px rgba(255,255,255,0.04);
        border-color: #888;
    }
}
"""