/* Tabulka výsledků závodníka - filtrování podle události a disciplíny, řazení.
 *
 * Data přicházejí hotová v šabloně (const DATA), takže se nikam nechodí
 * a celá tabulka se překresluje najednou - při dvaceti řádcích je to
 * levnější než cokoliv chytřejšího.
 *
 * Tlačítka událostí se berou z dat, ne ze seznamu v kódu. Když přibude
 * další typ šampionátu (EYMTBOC), objeví se sám a tady se nic needituje.
 */

'use strict';

(function () {
    const container = document.getElementById('results_table_container');
    if (!container || typeof DATA === 'undefined') {
        return;
    }

    // Pořadí událostí v liště - co v datech není, se přeskočí; co tu
    // není vyjmenované (nová událost), spadne podle abecedy na konec.
    const EVENT_ORDER = ['WMTBOC', 'EMTBOC', 'WCUP', 'JWMTBOC', 'EJMTBOC', 'EYMTBOC'];

    // Juniorské a youth šampionáty se odlišují barvou tlačítka, aby šlo
    // na první pohled poznat, která část kariéry je zrovna vidět.
    const JUNIOR_EVENTS = new Set(['JWMTBOC', 'EJMTBOC', 'EYMTBOC']);

    const COLUMNS = [
        { key: 'date', label: 'Date' },
        { key: 'result', label: 'Result' },
        { key: 'dist', label: 'Distance' },
        { key: 'event', label: 'Event' },
        { key: 'rtime', label: 'Time' },
    ];

    // Bez umístění (štafeta mimo hodnocení) - řadí se vždy na konec.
    const NO_PLACE = Number.MAX_SAFE_INTEGER;

    function byOrder(list, order) {
        return list.sort((a, b) => {
            const ia = order.indexOf(a);
            const ib = order.indexOf(b);
            if (ia === -1 && ib === -1) {
                return a.localeCompare(b);
            }
            return (ia === -1 ? order.length : ia) - (ib === -1 ? order.length : ib);
        });
    }

    const events = byOrder([...new Set(DATA.map((row) => row.event))], EVENT_ORDER);
    const distances = byOrder(
        [...new Set(DATA.map((row) => row.dist))],
        ['sprint', 'middle', 'long', 'mass_start', 'relay', 'mix_relay', 'sprint_relay']
    );

    // Zapnuté filtry. Na začátku je vidět všechno - hlavní smysl téhle
    // stránky je ukázat kariéru vcelku, včetně juniorských let.
    const state = {
        events: new Set(events),
        distances: new Set(distances),
        column: 'date',
        direction: 'desc',
    };

    function label(value) {
        return value.replace(/_/g, ' ');
    }

    function placeOf(row) {
        return row.result === null || row.result === undefined ? NO_PLACE : Number(row.result);
    }

    function compare(a, b) {
        const column = state.column;

        if (column === 'result') {
            return placeOf(a) - placeOf(b);
        }
        if (column === 'date') {
            return Date.parse(a.date) - Date.parse(b.date);
        }

        const va = (a[column] || '').toString().toLowerCase();
        const vb = (b[column] || '').toString().toLowerCase();
        if (va !== vb) {
            return va < vb ? -1 : 1;
        }

        // stejná hodnota - rozhodne umístění
        return placeOf(a) - placeOf(b);
    }

    function visibleRows() {
        const rows = DATA.filter(
            (row) => state.events.has(row.event) && state.distances.has(row.dist)
        ).sort(compare);

        return state.direction === 'desc' ? rows.reverse() : rows;
    }

    function button(text, active, extraClass, onClick) {
        const element = document.createElement('button');
        element.type = 'button';
        element.className = `btn btn-sm me-1 mb-1 btn-${active ? '' : 'outline-'}${extraClass}`;
        element.textContent = label(text);
        element.addEventListener('click', onClick);

        return element;
    }

    function toggle(set, key, all) {
        // Kliknutí na už jediný zapnutý filtr by nechalo prázdnou tabulku,
        // tak se místo toho zapne všechno zpátky.
        if (set.has(key)) {
            if (set.size === 1) {
                all.forEach((item) => set.add(item));
            } else {
                set.delete(key);
            }
        } else {
            set.add(key);
        }
    }

    function renderFilters(target) {
        target.innerHTML = '';

        const eventBar = document.createElement('div');
        eventBar.className = 'btn-toolbar mb-1';
        events.forEach((event) => {
            const colour = JUNIOR_EVENTS.has(event) ? 'info' : 'primary';
            eventBar.appendChild(
                button(event, state.events.has(event), colour, () => {
                    toggle(state.events, event, events);
                    render();
                })
            );
        });
        // "all" jen zapíná - vypínat všechno by nechalo prázdnou tabulku
        // a uživatel to stejně chce jako návrat do výchozího stavu.
        if (state.events.size < events.length) {
            eventBar.appendChild(
                button('show all', false, 'secondary', () => {
                    events.forEach((event) => state.events.add(event));
                    render();
                })
            );
        }

        const distBar = document.createElement('div');
        distBar.className = 'btn-toolbar mb-2';
        distances.forEach((dist) => {
            distBar.appendChild(
                button(dist, state.distances.has(dist), 'success', () => {
                    toggle(state.distances, dist, distances);
                    render();
                })
            );
        });
        if (state.distances.size < distances.length) {
            distBar.appendChild(
                button('show all', false, 'secondary', () => {
                    distances.forEach((dist) => state.distances.add(dist));
                    render();
                })
            );
        }

        target.appendChild(eventBar);
        target.appendChild(distBar);
    }

    function renderTable(target, rows) {
        target.innerHTML = '';

        const table = document.createElement('table');
        table.className = 'table table-hover table-sm';

        const head = document.createElement('tr');
        head.className = 'sortable';
        COLUMNS.forEach((column) => {
            const cell = document.createElement('th');
            cell.className = 'sortable';
            cell.textContent = column.label;

            const arrow = document.createElement('span');
            arrow.className = 'sort-direction';
            if (state.column === column.key) {
                arrow.classList.add(state.direction);
            }
            cell.appendChild(arrow);

            cell.addEventListener('click', () => {
                if (state.column === column.key) {
                    state.direction = state.direction === 'asc' ? 'desc' : 'asc';
                } else {
                    state.column = column.key;
                    state.direction = column.key === 'result' ? 'asc' : 'desc';
                }
                render();
            });

            head.appendChild(cell);
        });

        const thead = document.createElement('thead');
        thead.appendChild(head);
        table.appendChild(thead);

        const body = document.createElement('tbody');
        rows.forEach((row) => {
            const line = document.createElement('tr');
            if (JUNIOR_EVENTS.has(row.event)) {
                line.classList.add('junior-result');
            }

            const dateCell = document.createElement('td');
            const link = document.createElement('a');
            link.href = `/race/${row.race_id}/`;
            link.textContent = row.date;
            dateCell.appendChild(link);
            line.appendChild(dateCell);

            [
                row.result_label || (row.result === null || row.result === undefined ? '-' : row.result),
                label(row.dist),
                row.event,
                row.rtime || '',
            ].forEach((value) => {
                const cell = document.createElement('td');
                cell.textContent = value;
                line.appendChild(cell);
            });

            body.appendChild(line);
        });
        table.appendChild(body);

        if (!rows.length) {
            const empty = document.createElement('p');
            empty.className = 'text-muted';
            empty.textContent = 'No results for the selected filters.';
            target.appendChild(empty);
        }

        target.appendChild(table);
    }

    const filters = document.createElement('div');
    const table = document.createElement('div');
    container.appendChild(filters);
    container.appendChild(table);

    function render() {
        renderFilters(filters);
        renderTable(table, visibleRows());
    }

    render();
})();
