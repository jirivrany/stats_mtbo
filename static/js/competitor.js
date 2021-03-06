/* global $, Bloodhound */

(function($, Bloodhound){
    'use strict';
    var countries = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 10,
        prefetch: {
            url: '/api/prefetch/competitor/',
            filter: function(respo) {
                return respo.result;
            }
        }
    });

    var redirect = function redirect(event, datum) {
            console.log(event);
            var new_url = '/competitor/' + datum.id + '/';
            window.location.replace(new_url);
    };

    // kicks off the loading/processing of `local` and `prefetch`
    countries.initialize();

    $('#search')
        .typeahead(null, {
            name: 'countries',
            displayKey: 'name',
            source: countries.ttAdapter()
        })
        .on('typeahead:selected', redirect)
        .on('typeahead:autocompleted', redirect);

    
}($, Bloodhound));
