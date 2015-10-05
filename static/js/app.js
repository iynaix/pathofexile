// ANGULAR CONFIGURATION AND SETUP
angular.module("poe_app", []).config(['$interpolateProvider', function($interpolateProvider) {
    // prevent templating clashes
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

// CUSTOM FILTERS
angular.module("poe_app").filter('item_name_class', () => {
    return (item) => {
        // if item.is_gem()
        //     <span class="gem">
        // elif item.is_quest_item()
        //     <span class="quest">
        if (item.rarity !== "normal") { return item.rarity; }
        return "";
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

angular.module('poe_app').controller('BrowseCtrl', ['$http', function ($http) {
    let segments = window.location.pathname.split("/");
    let slug = segments[segments.length-2];
    this.items = [];

    $http.get(`/api/location/${slug}`).success((resp) => {
        this.items = resp;
    });
}]);
