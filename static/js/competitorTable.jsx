'use strict';

/**
 * Dynamically sets a deeply nested value in an object.
 * Optionally "bores" a path to it if its undefined.
 * @function
 * @param {!object} obj  - The object which contains the value you want to change/set.
 * @param {!array} path  - The array representation of path to the value you want to change/set.
 * @param {!mixed} value - The value you want to set it to.
 * @param {boolean} setrecursively - If true, will set value of non-existing path as well.
 */
function setDeep(obj, path, value, setrecursively = false) {

    let level = 0;

    path.reduce((a, b)=>{
        level++;

        if (setrecursively && typeof a[b] === "undefined" && level !== path.length){
            a[b] = {};
            return a[b];
        }

        if (level === path.length){
            a[b] = value;
            return value;
        } else {
            return a[b];
        }
    }, obj);
}


function sortString(a, b, column) {
    const nameA = a[column].toLowerCase(); // ignore upper and lowercase
    const nameB = b[column].toLowerCase(); // ignore upper and lowercase

    if (nameA < nameB) {
        return -1;
    }
    if (nameA > nameB) {
        return 1;
    }

    //  must be equal / sort by result
    return sortResult(a['result'], b['result']);
}


function sortResult(a, b) {
    return a-b;
}


function sortDate(a, b) {
    const dateA = Date.parse(a);
    const dateB = Date.parse(b);

    if (dateA < dateB) {
        return -1;
    }
    if (dateA > dateB) {
        return 1;
    }

    //  must be equal 
    return 0;

}



class ResultsRow extends React.Component {


    render() {
        const result = this.props.result;

        const trClass = Date.parse(result.expires) < Date.now() ? 'warning': '';
        const raceLink = "/race/" + result.race_id + "/";
        
        return (
            <tr className={trClass}>
            <td><a href={raceLink}>{result.date}</a></td>
            <td>{result.result}</td>
            <td>{result.dist}</td>
            <td>{result.event}</td>
          </tr>
        );
    }
}


class ResultsTable extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            sort: {
                column: null,
                direction: 'desc',
            }
        };
    }


    onSort = (column) => (e) => {
        const direction = this.state.sort.column ? (this.state.sort.direction === 'asc' ? 'desc': 'asc'): 'desc';

        const sort = {
            'column': column,
            'direction': direction
        };

        this.props.onSortKeyChange(sort);

        this.setState({
            sort: {
                column,
                direction,
            }
        });

    };

    setArrow = (column) => {
        let className = 'sort-direction';

        if (this.state.sort.column === column) {
            className += this.state.sort.direction === 'asc' ? ' asc': ' desc';
        }

        return className;
    };



    render() {

        let cels = [];

        const columns = this.props.columns;
      
        for (let col in columns) {
            cels.push(<th key={col} onClick={this.onSort(col)}>
                              {columns[col]}
                              <span className={this.setArrow(col)}></span>
                              </th>)
        }


        return (
            <table className="table table-hover" id={this.props.cssId}>
                 <thead>
                    <tr className="sortable">
                    {cels}
                    </tr>
                  </thead>
                  <tbody>{this.props.rows}</tbody>
                </table>
        );

    }
}


class TablesContainer extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            sortKey: this.props.sortKey,
            sortDirection: 'desc',
        };

        this.handleSortKeyChange = this.handleSortKeyChange.bind(this);
 
    }

    handleSortKeyChange(sort) {
        this.setState({
            sortKey: sort['column'],
            sortDirection: sort['direction']
        });
    }

    columns = {
            'date': 'Date',
            'result': 'Result',
            'dist': 'Distance',
            'event': 'Event'
            
    };



    render() {
        const results_rows = [];
        const column = Object.keys(this.columns).indexOf(this.state.sortKey) > -1 ? this.state.sortKey: 'date';
       
        let showEvents = [];
        let showDistances = [];

        for (let [key, value] of Object.entries(this.props.filter).slice(0,4)) {
          if (value === true) {
              showEvents.push(key);
          }
        }

        for (let [key, value] of Object.entries(this.props.filter).slice(4,)) {
          if (value === true) {
              showDistances.push(key);
          }
        }

       
        //filter out the results
        let sortedResults = this.props.data.filter((result) => {
            return showEvents.includes(result['event']);
        }).filter((result) => {
            return showDistances.includes(result['dist']);
        }).sort((a, b) => {
            if (column === 'date') {
                return sortDate(a[column], b[column]);
            }
            else if (column === 'result') {
                return sortResult(a[column], b[column]);
            }
             else {
                return sortString(a, b, column);
            }
        });
       
        if (this.state.sortDirection === 'desc') {
            sortedResults = sortedResults.reverse();
        }

     
        sortedResults.forEach((result) => {
            results_rows.push(
                <ResultsRow
                  sortKey={this.state.sortKey}
                  result={result}
                  key={result.date + result.dist + result.result}
                />
            );
        });

       
        return (
            <div className="container-fluid">
                <ResultsTable
                    columns={this.columns}
                    rows={results_rows}
                    onSortKeyChange={this.handleSortKeyChange}
                    />
                
            </div>
        );
    }
}


class Button extends React.Component {

    render() {
        const filterText = this.props.column;
        const iconProp = this.props.active === true ? 'ok': 'minus';
        const cssProp = this.props.active === true ? this.props.klasa : '';

        const css = "btn btn-" + cssProp + " btn-sm navbar-btn";
        const icon = "glyphicon glyphicon-" + iconProp;

        return (
            <button type="button" className={css} onClick={this.props.onClick}>{filterText} <span className={icon}></span></button>
        );

    }

}



class SearchBar extends React.Component {
    constructor(props) {
        super(props);
    }

    handleFilterButtonClick(source) {
        this.props.onFilterTextChange(source);
    }

    render() {


        let eventButtons = []
        let distButtons = []
        
        for (let [key, value] of Object.entries(this.props.buttonsState).slice(0,4)) {
            const klasa = key === 'all' ? 'warning' : 'primary';
            const button = <span key={key+value}>
                               &nbsp; 
                               <Button 
                                active={value}
                                column={key}
                                klasa={klasa}
                                onClick={this.handleFilterButtonClick.bind(this, key)}
                                 />  
                            </span>    
            eventButtons.push(button);
        }

        for (let [key, value] of Object.entries(this.props.buttonsState).slice(4,)) {
            const klasa = key === 'all_dist' ? 'warning' : 'success';
            const button = <span key={key+value}>
                               &nbsp; 
                               <Button 
                                active={value}
                                column={key}
                                klasa={klasa}
                                onClick={this.handleFilterButtonClick.bind(this, key)}
                                 />  
                            </span>    
            distButtons.push(button);
        }
        

        return (
            <div className="container-fluid">
                <div className="btn-toolbar" role="toolbar">
                    { eventButtons }
                </div>
                <div className="btn-toolbar" role="toolbar">
                    { distButtons }   
                </div>
            </div>
        );
    }
}

class FilterableTablesContainer extends React.Component {
    constructor(props) {
        super(props);
        const eventNames = ['WMTBOC', 'EMTBOC', 'WCUP'];
        
        
        this.state = {
            WMTBOC: true,
            EMTBOC: true,
            WCUP: true,
            all: true,
            long: true,
            mass_start: true,
            middle: true,
            mix_relay: true,
            relay: true,
            sprint: true,
            sprint_relay: true,
            all_dist: true
        };
        this.handleFilterButtonClick = this.handleFilterButtonClick.bind(this);
    }

    handleFilterButtonClick(source) {
        if (source==='all_dist') {
            this.setState((state, props) => ({
                [source]: !state[source],    
                long: !state[source],
                mass_start: !state[source],
                middle: !state[source],
                mix_relay: !state[source],
                relay: !state[source],
                sprint: !state[source],
                sprint_relay: !state[source]    
            }));
        }
        else if (source==='all') {
            this.setState((state, props) => ({
                [source]: !state[source],    
                WMTBOC: !state[source],
                EMTBOC: !state[source],
                WCUP: !state[source]
            }));
        }
        else {
            this.setState((state, props) => ({
              [source]: !state[source]
            }));
        }
        
        
    }

    render() {

       
        return (
         <div className="row">
             <SearchBar 
             onFilterTextChange={this.handleFilterButtonClick}
             buttonsState={this.state}
             />
              <TablesContainer
                data={this.props.data}
                filter={this.state}
              />
        </div>
        );
    }
}



const domContainer = document.querySelector('#results_table_container');
ReactDOM.render(<FilterableTablesContainer data={DATA} distances={DISTANCES} />, domContainer);