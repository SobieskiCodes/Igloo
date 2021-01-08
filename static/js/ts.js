$(function() {
    $("#members").tablesorter({
        theme: "blue",
        widthFixed: true,
        widgets: ["zebra", "filter"],
        headerTemplate: "{content}{icon}",
        sortMultiSortKey: "shiftKey",
        sortResetKey: 'ctrlKey'
    });

    $("#rackets").tablesorter({
        theme: "blue",
        widthFixed: true,
        widgets: ["zebra", "filter"],
        headerTemplate: "{content}{icon}",
        sortMultiSortKey: "shiftKey",
        sortResetKey: 'ctrlKey'
    });
     $("#employees").tablesorter({
        theme: "blue",
        widthFixed: true,
        widgets: ["zebra", "filter"],
        headerTemplate: "{content}{icon}",
        sortMultiSortKey: "shiftKey",
        sortResetKey: 'ctrlKey'
    });
      $("#organizedc").tablesorter({
        theme: "blue",
        widthFixed: true,
        widgets: ["zebra", "filter"],
        headerTemplate: "{content}{icon}",
        sortMultiSortKey: "shiftKey",
        sortResetKey: 'ctrlKey'
    });
});
