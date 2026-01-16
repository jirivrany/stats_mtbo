/* Modern VanillaJS + React - Competitor Results Table */
/* globals React, ReactDOM, document */

'use strict';

// Helper function for multi-level sorting
const firstBy = (function() {
    /* mixin for the `thenBy` property */
    function extend(f) {
        f.thenBy = tb;
        return f;
    }
    /* adds a secondary compare function to the target function (`this` context)
       which is applied in case the first one returns 0 (equal)
       returns a new compare function, which has a `thenBy` method as well */
    function tb(y) {
        const x = this;
        return extend(function(a, b) {
            return x(a,b) || y(a,b);
        });
    }
    return extend;
})();

// Sorting functions
const sortByDistance = (a, b) => a.dist.localeCompare(b.dist);

const sortByPlace = (a, b) => parseInt(a.result) - parseInt(b.result);

const sortByEvent = (a, b) => a.event.localeCompare(b.event);

const sortByDate = (a, b) => {
    const s1 = a.date.split("/");
    const s2 = b.date.split("/");
    const d1 = new Date(s1[1] + " " + s1[0] + " " + s1[2]);
    const d2 = new Date(s2[1] + " " + s2[0] + " " + s2[2]);
    return d2 - d1;
};

const sorters = [sortByDate, sortByPlace, sortByDistance, sortByEvent];

/**
 * ResultTable Component - Displays sortable competitor results
 */
class ResultTable extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            sorting: 1  // Default sort by place (result)
        };
    }

    handleClick = (sorter) => {
        this.setState({ sorting: sorter });
    }

    render() {
        // Sort the rows based on current sorting selection
        if (this.state.sorting !== 1) {
            this.props.rows.sort(firstBy(sorters[this.state.sorting]).thenBy(sortByPlace));
        } else {
            this.props.rows.sort(sorters[this.state.sorting]);
        }

        const tableRows = this.props.rows.map((row) => {
            return React.createElement("tr", { key: row.race_id },
                React.createElement("td", null,
                    React.createElement("a", { href: "/race/" + row.race_id },
                        row.date
                    )
                ),
                React.createElement("td", null, row.result),
                React.createElement("td", null, row.dist),
                React.createElement("td", null, row.event),
                React.createElement("td", null, row.rtime)
            );
        });

        return React.createElement("table", { className: "table-condensed" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", {
                        className: "sortable",
                        onClick: () => this.handleClick(0)
                    }, "Date"),
                    React.createElement("th", {
                        className: "sortable",
                        onClick: () => this.handleClick(1)
                    }, "Result"),
                    React.createElement("th", {
                        className: "sortable",
                        onClick: () => this.handleClick(2)
                    }, "Race"),
                    React.createElement("th", {
                        className: "sortable",
                        onClick: () => this.handleClick(3)
                    }, "Event"),
                    React.createElement("th", null, "Time")
                )
            ),
            React.createElement("tbody", null, tableRows)
        );
    }
}

/**
 * ResultBox Component - Container that fetches and displays competitor results
 */
class ResultBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [],
            loading: true,
            error: null
        };
    }

    async loadResultsFromServer() {
        try {
            // Get competitor ID from data attribute (VanillaJS replacement for jQuery)
            const competitorElement = document.getElementById('competitor');
            const cid = competitorElement ? competitorElement.dataset.cid : null;

            if (!cid) {
                throw new Error('Competitor ID not found');
            }

            const url = `/api/competitor/${cid}/`;

            // Modern fetch API (replacement for $.ajax)
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            this.setState({
                data: data.result || [],
                loading: false
            });
        } catch (error) {
            console.error('Error loading results:', error);
            this.setState({
                error: error.message,
                loading: false
            });
        }
    }

    componentDidMount() {
        this.loadResultsFromServer();
    }

    render() {
        const { data, loading, error } = this.state;

        if (loading) {
            return React.createElement("div", { className: "ResultBox" },
                React.createElement("p", null, "Loading results...")
            );
        }

        if (error) {
            return React.createElement("div", { className: "ResultBox alert alert-danger" },
                React.createElement("p", null, "Error loading results: ", error)
            );
        }

        return React.createElement("div", { className: "ResultBox" },
            React.createElement(ResultTable, { rows: data })
        );
    }
}

// Initialize when DOM is ready
(function() {
    const competitorElement = document.getElementById('competitor');
    if (competitorElement) {
        // Modern ReactDOM.render (replacement for deprecated React.render)
        ReactDOM.render(
            React.createElement(ResultBox, null),
            competitorElement
        );
    }
})();
