/* Modern VanillaJS Competitor Search with Autocomplete */

(function() {
    'use strict';

    // Cache for competitors data
    let competitorsData = [];
    let dropdown = null;
    let searchInput = null;
    let selectedIndex = -1;

    /**
     * Fetch competitors from API
     */
    async function fetchCompetitors() {
        try {
            const response = await fetch('/api/prefetch/competitor/');
            const data = await response.json();
            competitorsData = data.result || [];
            initializeAutocomplete();
        } catch (error) {
            console.error('Error fetching competitors:', error);
        }
    }

    /**
     * Initialize autocomplete functionality
     */
    function initializeAutocomplete() {
        searchInput = document.getElementById('search');
        if (!searchInput) return;

        searchInput.setAttribute('autocomplete', 'off');

        // Create custom dropdown
        dropdown = document.createElement('div');
        dropdown.id = 'competitors-dropdown';
        dropdown.style.cssText = `
            position: absolute;
            background: white;
            border: 1px solid #ccc;
            max-height: 300px;
            overflow-y: auto;
            display: none;
            z-index: 1000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;

        // Position dropdown relative to input
        searchInput.parentNode.style.position = 'relative';
        searchInput.parentNode.appendChild(dropdown);

        // Event listeners
        searchInput.addEventListener('input', handleInput);
        searchInput.addEventListener('keydown', handleKeydown);
        searchInput.addEventListener('blur', () => {
            // Delay to allow click on dropdown item
            setTimeout(() => hideDropdown(), 150);
        });
        searchInput.addEventListener('focus', handleInput);
    }

    /**
     * Handle input changes - show dropdown only when at least 1 character is typed
     */
    function handleInput() {
        const searchValue = searchInput.value.trim();

        if (searchValue.length < 1) {
            hideDropdown();
            return;
        }

        const searchLower = searchValue.toLowerCase();
        const matches = competitorsData.filter(c =>
            c.name.toLowerCase().includes(searchLower)
        ).slice(0, 50); // Limit results for performance

        if (matches.length > 0) {
            showDropdown(matches);
        } else {
            hideDropdown();
        }
    }

    /**
     * Show dropdown with matching competitors
     */
    function showDropdown(matches) {
        dropdown.innerHTML = '';
        selectedIndex = -1;

        matches.forEach((competitor, index) => {
            const item = document.createElement('div');
            item.textContent = competitor.name;
            item.setAttribute('data-id', competitor.id);
            item.setAttribute('data-index', index);
            item.style.cssText = `
                padding: 8px 12px;
                cursor: pointer;
                color: black;
                background: white;
            `;
            item.addEventListener('mouseenter', () => {
                item.style.background = '#f0f0f0';
            });
            item.addEventListener('mouseleave', () => {
                item.style.background = 'white';
            });
            item.addEventListener('mousedown', (e) => {
                e.preventDefault();
                redirectToCompetitor(competitor.id);
            });
            dropdown.appendChild(item);
        });

        // Position and show dropdown
        dropdown.style.width = searchInput.offsetWidth + 'px';
        dropdown.style.display = 'block';
    }

    /**
     * Hide dropdown
     */
    function hideDropdown() {
        if (dropdown) {
            dropdown.style.display = 'none';
            selectedIndex = -1;
        }
    }

    /**
     * Handle keyboard navigation
     */
    function handleKeydown(event) {
        const items = dropdown.querySelectorAll('div');

        if (event.key === 'ArrowDown') {
            event.preventDefault();
            if (selectedIndex < items.length - 1) {
                selectedIndex++;
                updateSelection(items);
            }
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            if (selectedIndex > 0) {
                selectedIndex--;
                updateSelection(items);
            }
        } else if (event.key === 'Enter') {
            event.preventDefault();
            if (selectedIndex >= 0 && items[selectedIndex]) {
                const id = items[selectedIndex].getAttribute('data-id');
                redirectToCompetitor(id);
            } else {
                // Try to find a match from current input
                const searchValue = searchInput.value.trim();
                if (searchValue.length >= 1) {
                    const searchLower = searchValue.toLowerCase();
                    const competitor = competitorsData.find(c =>
                        c.name.toLowerCase().includes(searchLower)
                    );
                    if (competitor) {
                        redirectToCompetitor(competitor.id);
                    }
                }
            }
        } else if (event.key === 'Escape') {
            hideDropdown();
        }
    }

    /**
     * Update visual selection in dropdown
     */
    function updateSelection(items) {
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.style.background = '#f0f0f0';
            } else {
                item.style.background = 'white';
            }
        });

        // Scroll into view if needed
        if (items[selectedIndex]) {
            items[selectedIndex].scrollIntoView({ block: 'nearest' });
        }
    }

    /**
     * Redirect to competitor page
     */
    function redirectToCompetitor(competitorId) {
        const url = `/competitor/${competitorId}/`;
        window.location.href = url;
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fetchCompetitors);
    } else {
        fetchCompetitors();
    }

})();
