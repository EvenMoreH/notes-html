# search script to be injected into index.html
SEARCH_SCRIPT = """<script>
        (function() {{
            const input = document.getElementById('search');
            const resultsContainer = document.getElementById('results');
            const noResults = document.getElementById('no-results');

            function filterNotes(q) {{
                const query = q.trim().toLowerCase();
                const items = Array.from(resultsContainer.querySelectorAll('.note-item'));
                if (!query) {{
                    items.forEach(i => i.style.display = '');
                    noResults.style.display = 'none';
                    return;
                }}
                let anyVisible = false;
                items.forEach(item => {{
                    const text = item.textContent.toLowerCase();
                    const matched = text.indexOf(query) !== -1;
                    item.style.display = matched ? '' : 'none';
                    if (matched) anyVisible = true;
                }});
                noResults.style.display = anyVisible ? 'none' : '';
            }}

            input.addEventListener('input', function(e) {{
                filterNotes(e.target.value);
            }});
        }})();
        </script>"""