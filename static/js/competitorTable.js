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

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance"); }

function _iterableToArrayLimit(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _instanceof(left, right) { if (right != null && typeof Symbol !== "undefined" && right[Symbol.hasInstance]) { return right[Symbol.hasInstance](left); } else { return left instanceof right; } }

function _typeof(obj) { if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _classCallCheck(instance, Constructor) { if (!_instanceof(instance, Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function setDeep(obj, path, value) {
  var setrecursively = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : false;
  var level = 0;
  path.reduce(function (a, b) {
    level++;

    if (setrecursively && typeof a[b] === "undefined" && level !== path.length) {
      a[b] = {};
      return a[b];
    }

    if (level === path.length) {
      a[b] = value;
      return value;
    } else {
      return a[b];
    }
  }, obj);
}

function sortString(a, b, column) {
  var nameA = a[column].toLowerCase(); // ignore upper and lowercase

  var nameB = b[column].toLowerCase(); // ignore upper and lowercase

  if (nameA < nameB) {
    return -1;
  }

  if (nameA > nameB) {
    return 1;
  } //  must be equal / sort by result


  return sortResult(a['result'], b['result']);
}

function sortResult(a, b) {
  return a - b;
}

function sortDate(a, b) {
  var dateA = Date.parse(a);
  var dateB = Date.parse(b);

  if (dateA < dateB) {
    return -1;
  }

  if (dateA > dateB) {
    return 1;
  } //  must be equal 


  return 0;
}

var ResultsRow =
/*#__PURE__*/
function (_React$Component) {
  _inherits(ResultsRow, _React$Component);

  function ResultsRow() {
    _classCallCheck(this, ResultsRow);

    return _possibleConstructorReturn(this, _getPrototypeOf(ResultsRow).apply(this, arguments));
  }

  _createClass(ResultsRow, [{
    key: "render",
    value: function render() {
      var result = this.props.result;
      var trClass = Date.parse(result.expires) < Date.now() ? 'warning' : '';
      var raceLink = "/race/" + result.race_id + "/";
      return React.createElement("tr", {
        className: trClass
      }, React.createElement("td", null, React.createElement("a", {
        href: raceLink
      }, result.date)), React.createElement("td", null, result.result), React.createElement("td", null, result.dist), React.createElement("td", null, result.event));
    }
  }]);

  return ResultsRow;
}(React.Component);

var ResultsTable =
/*#__PURE__*/
function (_React$Component2) {
  _inherits(ResultsTable, _React$Component2);

  function ResultsTable(props) {
    var _this;

    _classCallCheck(this, ResultsTable);

    _this = _possibleConstructorReturn(this, _getPrototypeOf(ResultsTable).call(this, props));

    _defineProperty(_assertThisInitialized(_this), "onSort", function (column) {
      return function (e) {
        var direction = _this.state.sort.column ? _this.state.sort.direction === 'asc' ? 'desc' : 'asc' : 'desc';
        var sort = {
          'column': column,
          'direction': direction
        };

        _this.props.onSortKeyChange(sort);

        _this.setState({
          sort: {
            column: column,
            direction: direction
          }
        });
      };
    });

    _defineProperty(_assertThisInitialized(_this), "setArrow", function (column) {
      var className = 'sort-direction';

      if (_this.state.sort.column === column) {
        className += _this.state.sort.direction === 'asc' ? ' asc' : ' desc';
      }

      return className;
    });

    _this.state = {
      sort: {
        column: null,
        direction: 'desc'
      }
    };
    return _this;
  }

  _createClass(ResultsTable, [{
    key: "render",
    value: function render() {
      var cels = [];
      var columns = this.props.columns;

      for (var col in columns) {
        cels.push(React.createElement("th", {
          key: col,
          onClick: this.onSort(col)
        }, columns[col], React.createElement("span", {
          className: this.setArrow(col)
        })));
      }

      return React.createElement("table", {
        className: "table table-hover",
        id: this.props.cssId
      }, React.createElement("thead", null, React.createElement("tr", {
        className: "sortable"
      }, cels)), React.createElement("tbody", null, this.props.rows));
    }
  }]);

  return ResultsTable;
}(React.Component);

var TablesContainer =
/*#__PURE__*/
function (_React$Component3) {
  _inherits(TablesContainer, _React$Component3);

  function TablesContainer(props) {
    var _this2;

    _classCallCheck(this, TablesContainer);

    _this2 = _possibleConstructorReturn(this, _getPrototypeOf(TablesContainer).call(this, props));

    _defineProperty(_assertThisInitialized(_this2), "columns", {
      'date': 'Date',
      'result': 'Result',
      'dist': 'Distance',
      'event': 'Event'
    });

    _this2.state = {
      sortKey: _this2.props.sortKey,
      sortDirection: 'desc'
    };
    _this2.handleSortKeyChange = _this2.handleSortKeyChange.bind(_assertThisInitialized(_this2));
    return _this2;
  }

  _createClass(TablesContainer, [{
    key: "handleSortKeyChange",
    value: function handleSortKeyChange(sort) {
      this.setState({
        sortKey: sort['column'],
        sortDirection: sort['direction']
      });
    }
  }, {
    key: "render",
    value: function render() {
      var _this3 = this;

      var results_rows = [];
      var column = Object.keys(this.columns).indexOf(this.state.sortKey) > -1 ? this.state.sortKey : 'date';
      var showEvents = [];
      var showDistances = [];
      var _iteratorNormalCompletion = true;
      var _didIteratorError = false;
      var _iteratorError = undefined;

      try {
        for (var _iterator = Object.entries(this.props.filter).slice(0, 4)[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
          var _step$value = _slicedToArray(_step.value, 2),
              key = _step$value[0],
              value = _step$value[1];

          if (value === true) {
            showEvents.push(key);
          }
        }
      } catch (err) {
        _didIteratorError = true;
        _iteratorError = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion && _iterator.return != null) {
            _iterator.return();
          }
        } finally {
          if (_didIteratorError) {
            throw _iteratorError;
          }
        }
      }

      var _iteratorNormalCompletion2 = true;
      var _didIteratorError2 = false;
      var _iteratorError2 = undefined;

      try {
        for (var _iterator2 = Object.entries(this.props.filter).slice(4)[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
          var _step2$value = _slicedToArray(_step2.value, 2),
              key = _step2$value[0],
              value = _step2$value[1];

          if (value === true) {
            showDistances.push(key);
          }
        } //filter out the results

      } catch (err) {
        _didIteratorError2 = true;
        _iteratorError2 = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion2 && _iterator2.return != null) {
            _iterator2.return();
          }
        } finally {
          if (_didIteratorError2) {
            throw _iteratorError2;
          }
        }
      }

      var sortedResults = this.props.data.filter(function (result) {
        return showEvents.includes(result['event']);
      }).filter(function (result) {
        return showDistances.includes(result['dist']);
      }).sort(function (a, b) {
        if (column === 'date') {
          return sortDate(a[column], b[column]);
        } else if (column === 'result') {
          return sortResult(a[column], b[column]);
        } else {
          return sortString(a, b, column);
        }
      });

      if (this.state.sortDirection === 'desc') {
        sortedResults = sortedResults.reverse();
      }

      sortedResults.forEach(function (result) {
        results_rows.push(React.createElement(ResultsRow, {
          sortKey: _this3.state.sortKey,
          result: result,
          key: result.date + result.dist + result.result
        }));
      });
      return React.createElement("div", {
        className: "container-fluid"
      }, React.createElement(ResultsTable, {
        columns: this.columns,
        rows: results_rows,
        onSortKeyChange: this.handleSortKeyChange
      }));
    }
  }]);

  return TablesContainer;
}(React.Component);

var Button =
/*#__PURE__*/
function (_React$Component4) {
  _inherits(Button, _React$Component4);

  function Button() {
    _classCallCheck(this, Button);

    return _possibleConstructorReturn(this, _getPrototypeOf(Button).apply(this, arguments));
  }

  _createClass(Button, [{
    key: "render",
    value: function render() {
      var filterText = this.props.column;
      var iconProp = this.props.active === true ? 'ok' : 'minus';
      var cssProp = this.props.active === true ? this.props.klasa : '';
      var css = "btn btn-" + cssProp + " btn-sm navbar-btn";
      var icon = "glyphicon glyphicon-" + iconProp;
      return React.createElement("button", {
        type: "button",
        className: css,
        onClick: this.props.onClick
      }, filterText, " ", React.createElement("span", {
        className: icon
      }));
    }
  }]);

  return Button;
}(React.Component);

var SearchBar =
/*#__PURE__*/
function (_React$Component5) {
  _inherits(SearchBar, _React$Component5);

  function SearchBar(props) {
    _classCallCheck(this, SearchBar);

    return _possibleConstructorReturn(this, _getPrototypeOf(SearchBar).call(this, props));
  }

  _createClass(SearchBar, [{
    key: "handleFilterButtonClick",
    value: function handleFilterButtonClick(source) {
      this.props.onFilterTextChange(source);
    }
  }, {
    key: "render",
    value: function render() {
      var eventButtons = [];
      var distButtons = [];
      var _iteratorNormalCompletion3 = true;
      var _didIteratorError3 = false;
      var _iteratorError3 = undefined;

      try {
        for (var _iterator3 = Object.entries(this.props.buttonsState).slice(0, 4)[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
          var _step3$value = _slicedToArray(_step3.value, 2),
              key = _step3$value[0],
              value = _step3$value[1];

          var klasa = key === 'all' ? 'warning' : 'primary';
          var button = React.createElement("span", {
            key: key + value
          }, "\xA0", React.createElement(Button, {
            active: value,
            column: key,
            klasa: klasa,
            onClick: this.handleFilterButtonClick.bind(this, key)
          }));
          eventButtons.push(button);
        }
      } catch (err) {
        _didIteratorError3 = true;
        _iteratorError3 = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion3 && _iterator3.return != null) {
            _iterator3.return();
          }
        } finally {
          if (_didIteratorError3) {
            throw _iteratorError3;
          }
        }
      }

      var _iteratorNormalCompletion4 = true;
      var _didIteratorError4 = false;
      var _iteratorError4 = undefined;

      try {
        for (var _iterator4 = Object.entries(this.props.buttonsState).slice(4)[Symbol.iterator](), _step4; !(_iteratorNormalCompletion4 = (_step4 = _iterator4.next()).done); _iteratorNormalCompletion4 = true) {
          var _step4$value = _slicedToArray(_step4.value, 2),
              key = _step4$value[0],
              value = _step4$value[1];

          var _klasa = key === 'all_dist' ? 'warning' : 'success';

          var _button = React.createElement("span", {
            key: key + value
          }, "\xA0", React.createElement(Button, {
            active: value,
            column: key,
            klasa: _klasa,
            onClick: this.handleFilterButtonClick.bind(this, key)
          }));

          distButtons.push(_button);
        }
      } catch (err) {
        _didIteratorError4 = true;
        _iteratorError4 = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion4 && _iterator4.return != null) {
            _iterator4.return();
          }
        } finally {
          if (_didIteratorError4) {
            throw _iteratorError4;
          }
        }
      }

      return React.createElement("div", {
        className: "container-fluid"
      }, React.createElement("div", {
        className: "btn-toolbar",
        role: "toolbar"
      }, eventButtons), React.createElement("div", {
        className: "btn-toolbar",
        role: "toolbar"
      }, distButtons));
    }
  }]);

  return SearchBar;
}(React.Component);

var FilterableTablesContainer =
/*#__PURE__*/
function (_React$Component6) {
  _inherits(FilterableTablesContainer, _React$Component6);

  function FilterableTablesContainer(props) {
    var _this4;

    _classCallCheck(this, FilterableTablesContainer);

    _this4 = _possibleConstructorReturn(this, _getPrototypeOf(FilterableTablesContainer).call(this, props));
    var eventNames = ['WMTBOC', 'EMTBOC', 'WCUP'];
    _this4.state = {
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
    _this4.handleFilterButtonClick = _this4.handleFilterButtonClick.bind(_assertThisInitialized(_this4));
    return _this4;
  }

  _createClass(FilterableTablesContainer, [{
    key: "handleFilterButtonClick",
    value: function handleFilterButtonClick(source) {
      if (source === 'all_dist') {
        this.setState(function (state, props) {
          var _ref;

          return _ref = {}, _defineProperty(_ref, source, !state[source]), _defineProperty(_ref, "long", !state[source]), _defineProperty(_ref, "mass_start", !state[source]), _defineProperty(_ref, "middle", !state[source]), _defineProperty(_ref, "mix_relay", !state[source]), _defineProperty(_ref, "relay", !state[source]), _defineProperty(_ref, "sprint", !state[source]), _defineProperty(_ref, "sprint_relay", !state[source]), _ref;
        });
      } else if (source === 'all') {
        this.setState(function (state, props) {
          var _ref2;

          return _ref2 = {}, _defineProperty(_ref2, source, !state[source]), _defineProperty(_ref2, "WMTBOC", !state[source]), _defineProperty(_ref2, "EMTBOC", !state[source]), _defineProperty(_ref2, "WCUP", !state[source]), _ref2;
        });
      } else {
        this.setState(function (state, props) {
          return _defineProperty({}, source, !state[source]);
        });
      }
    }
  }, {
    key: "render",
    value: function render() {
      return React.createElement("div", {
        className: "row"
      }, React.createElement(SearchBar, {
        onFilterTextChange: this.handleFilterButtonClick,
        buttonsState: this.state
      }), React.createElement(TablesContainer, {
        data: this.props.data,
        filter: this.state
      }));
    }
  }]);

  return FilterableTablesContainer;
}(React.Component);

var domContainer = document.querySelector('#results_table_container');
ReactDOM.render(React.createElement(FilterableTablesContainer, {
  data: DATA,
  distances: DISTANCES
}), domContainer);