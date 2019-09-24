       function get_last(data) {
            var minutes = 0;
            if (data.last_action.relative.indexOf('hour') > 0) {
                minutes = parseInt(data.last_action.relative.split(' ')[0]) * 60;
            } else if (data.last_action.relative.indexOf('day') > 0) {
                minutes = parseInt(data.last_action.relative.split(' ')[0]) * 60 * 24;
            } else if (data.last_action.relative.indexOf('minute') > 0) {
                minutes = parseInt(data.last_action.relative.split(' ')[0]);
            }
            return minutes + "";
        }

        function get_status(data) {
            var status = "Okay";
            if (data.basicicons.icon71) {
                status = "Trav";
            }
            if (data.basicicons.icon15) {
                status = "Hosp";
            }
            if (data.basicicons.icon16) {
                status = "Jail";
            }

            return status;
        }

        var queue = [];
        function update_player() {
            if (queue.length > 0) {
                var player_id = queue.shift();
                $.get('https://api.torn.com/user/' + player_id + '?selections=profile&key=' + $('#api-key').val(), function(data, status){
                    var col1 = $('#' + player_id + ' td')[0];
                    var col2 = $('#' + player_id + ' td')[1];
                    $(col1).text(get_last(data));
                    $("#players").trigger("updateCell", [col1, false]);
                    $(col2).text(get_status(data));
                    $("#players").trigger("updateCell", [col2, false]);
                });
            }
        }

        function queue_player(player_id) {
            queue.push(player_id);
        }

        setInterval(update_player, 1200);

        $(function() {
            $("#members").tablesorter({
                theme: "blue",
                widthFixed: true,
                widgets: ["zebra", "filter"],
                headerTemplate: "{content}{icon}",
                sortMultiSortKey: "shiftKey",
                sortResetKey: 'ctrlKey'
            });

            $("#check_form").submit(function(e){
                e.preventDefault();
                var visible = $('.player').not('.filtered');
                var limit = 50;
                for (var i = 0; i < visible.length && i < limit; i++) {
                    queue_player(visible[i].id);
                }
            });
        });