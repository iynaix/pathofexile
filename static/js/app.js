'use strict';

// ANGULAR CONFIGURATION AND SETUP
angular.module("poe_app", []).config(['$interpolateProvider', function($interpolateProvider) {
    // prevent templating clashes
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

// CUSTOM FILTERS
angular.module("poe_app").filter('item_name_class', () => {
    return (item) => {
        switch (item.rarity) {
            case "gem":
                return "gem";
            case "quest":
                return "quest";
            case "magic":
                return "magic";
            case "rare":
                return "rare";
            case "unique":
                return "unique";
            default:
                return "normal";
        }
        if (item.rarity !== "normal") { return item.rarity; }
    }
}).filter('sockets', ['$sce', ($sce) => {
    return (socket_str) => {
        let ret = [].map.call(socket_str, (c) => {
            switch (c) {
                case "B":
                    return '<span class="label label-primary">&nbsp;</span>';
                case "G":
                    return '<span class="label label-success">&nbsp;</span>';
                case "R":
                    return '<span class="label label-danger">&nbsp;</span>';
                default:
                    return '&nbsp;';
            }
        });
        return $sce.trustAsHtml(ret.join("&#8202;"));
    }
}]);

// CUSTOM DIRECTIVES
angular.module('poe_app').directive('poeItemTitle', ['socketsFilter', function(sockets) {
    return {
        restrict: 'A',
        scope: {
            item: '='
        },
        replace: true,
        link: (scope, elem, attrs) => {
            // default to showing sockets
            scope.sockets = true;
            if ((attrs.sockets===false)||(attrs.sockets==="false")) {
                scope.sockets = false;
            }
        },
        template: `
            <h4 ng-class="{item_popover: item.item_popover, unindentified: !item.is_identified}">
                <span ng-if="item.name" ng-class="item|item_name_class">[[ item.name ]]</span>
                <span ng-if="sockets && item.socket_str" style="margin-left: 1em;" ng-bind-html="item.socket_str|sockets"></span>
                <br/>
                <span ng-class="{magic: item.rarity==='magic'}">[[ item.type ]]</span>
                <span ng-if="sockets && item.socket_str && !item.name" style="margin-left: 1em;" ng-bind-html="item.socket_str|sockets"></span>
            </h4>`
    };
}]);

angular.module('poe_app').controller('BrowseCtrl', ['$http', function ($http) {
    let segments = window.location.pathname.split("/");
    let slug = segments[segments.length-2];
    this.items = [];

    $http.get(`/api/location/${slug}`).success((resp) => {
        this.items = resp;
    });
}]);
