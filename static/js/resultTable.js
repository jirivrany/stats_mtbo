/* globals React, document, data */
var firstBy = (function() {
    /* mixin for the `thenBy` property */
    function extend(f) {
        f.thenBy = tb;
        return f;
    }
    /* adds a secondary compare function to the target function (`this` context)
       which is applied in case the first one returns 0 (equal)
       returns a new compare function, which has a `thenBy` method as well */
    function tb(y) {
        var x = this;
        return extend(function(a, b) {
            return x(a,b) || y(a,b);
        });
    }
    return extend;
})();


(function(){

    "use strict";

var sortByDistance = function sortByDistance(a, b) {
    return a.dist.localeCompare(b.dist);
};

var sortByPlace = function sortByPlace(a, b) {
  return parseInt(a.result) - parseInt(b.result);
};

var sortByEvent = function sortByEvent(a, b) {
    return a.event.localeCompare(b.event);
};

var sortByDate = function sortByDate(a, b) {
    var d1, d2, s1, s2;
    s1 = a.date.split("/");
    s2 = b.date.split("/");
    d1 = new Date(s1[1] + " " + s1[0] + " " +s1[2]);
    d2 = new Date(s2[1] + " " + s2[0] + " " +s2[2]);
    return  d2 - d1;
};

var sorters = [sortByDate, sortByPlace, sortByDistance, sortByEvent];

var ResultTable = React.createClass({displayName: "ResultTable",

    getInitialState: function(){
        return {
          sorting: 1
        };
    },


    handleClick: function(sorter) {
        this.setState({sorting: sorter});
    },

    render: function() {

        if (this.state.sorting != 1) {
            this.props.rows.sort(firstBy(sorters[this.state.sorting]).thenBy(sortByPlace));
        }
        else {
            this.props.rows.sort(sorters[this.state.sorting]);
        }        
        
        
        var tableRows = this.props.rows.map(function(row){
            return (React.createElement("tr", {key: row.race_id}, 
                React.createElement("td", null,  row.date), 
                React.createElement("td", null,  row.result), 
                React.createElement("td", null,  row.dist), 
                React.createElement("td", null,  row.event), 
                React.createElement("td", null,  row.rtime)
                ));
        });


        return (
            React.createElement("table", {className: "table-condensed"}, 
            React.createElement("thead", null, 
            React.createElement("tr", null, 
            React.createElement("th", {className: "sortable", onClick: this.handleClick.bind(null, 0)}, "Date"
            ), 
            React.createElement("th", {className: "sortable", onClick: this.handleClick.bind(null, 1)}, "Result"
            ), 
            React.createElement("th", {className: "sortable", onClick: this.handleClick.bind(null, 2)}, "Race"
            ), 
            React.createElement("th", {className: "sortable", onClick: this.handleClick.bind(null, 3)}, "Event"
            ), 
            React.createElement("th", null, "Time")
            )
            ), 
            React.createElement("tbody", null, 
                tableRows
            )
            )
        );
    }
});


var ResultBox = React.createClass({displayName: "ResultBox",
    loadResultsFromServer: function() {
        var cid, myurl;

        cid = $('#competitor').data('cid');
        myurl = '/api/competitor/' + cid +'/';
        
        $.ajax({
            url: myurl,
            dataType: 'json',
            success: function(data) {
                this.setState({
                    data: data.result
                });
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },

    getInitialState: function() {
        return {
            data: [] 
        };
    },
    componentDidMount: function() {
        this.loadResultsFromServer();
    },

    render: function() {
        return (
            React.createElement("div", {className: "ResultBox"}, 
            React.createElement(ResultTable, {rows: this.state.data})
            )
        );
    }
});


React.render( React.createElement(ResultBox, null),
    document.getElementById('competitor')
);
}());