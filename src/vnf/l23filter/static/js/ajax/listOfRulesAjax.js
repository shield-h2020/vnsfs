// Get last test result
function getListOfRulesAjax(callback) {
    $.ajax({
        type: 'POST',
        url:  '/getFlow/v2',
        dataType: "json",
        data: JSON.stringify({}),
        success: function(data)
        {
            if( callback ) callback(data);
        },
        error: function(err)
        {
           console.log("Error!!!");
        }
    });
}

function deleteFlowAjax(callback, thisButton) {
    // console.log(thisButton);
    $.ajax({
        type: 'DELETE',
        url:  '/deleteFlow/v2?id=' + thisButton.attr("flow_id"),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function(data)
        {
            if( callback ) callback(data);
        },
        error: function(err)
        {
           console.log("Error!!!");
        }
    });
}

function startFirewall(callback) {
    $.ajax({
        type: 'GET',
        url:  '/startFirewall',
        // dataType: "json",
        success: function(data)
        {
            if( callback ) callback(data);
        },
        error: function(err)
        {
           console.log("Error!!!");
        }
    });
}

function stopFirewall(callback) {
    $.ajax({
        type: 'GET',
        url:  '/stopFirewall',
        // dataType: "json",
        success: function(data)
        {
            if( callback ) callback(data);
        },
        error: function(err)
        {
           console.log("Error!!!");
        }
    });
}

function getFirewallStatus(callback) {
    $.ajax({
        type: 'GET',
        url:  '/getFirewallStatus',
        // dataType: "json",
        success: function(data)
        {
            if( callback ) callback(data);
        },
        error: function(err)
        {
           console.log("Error!!!");
        }
    });
}