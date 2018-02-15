function replaceIfNull(varToCheck, replaceWith){
    return ((varToCheck == null) ? replaceWith : varToCheck);
}

function actionsHandler(actions){
    var stringToPrint = "";
    if (actions != null && typeof actions[0]  != "string") {
        console.log(actions.length);
        // console.log(actions[1]);
        for (var i = 0; i < actions.length; i++) {
            stringToPrint += "<p>\"" + Object.keys(actions[i])[0] + "\"" + " : " + actions[i][Object.keys(actions[i])[0]] + "</p>";
        }
        console.log(stringToPrint);
        return stringToPrint;
    }
    else{
        return actions;
    }

}

function printFlows(){
    getListOfRulesAjax(function(json_file){
        $(".table_body").empty();
        for (var i=0 ; i < json_file.length ; i++ ){

            // console.log(json_file[i]);
            // console.log(Object.keys(json_file[i]["actions"][0]));

            var row_class = "warning";
            var status = "<button class=\"btn btn-warning btn-circle\" type=\"button\"><i class=\"fa fa-spinner fa-spin\"></i></button>"

            if (json_file[i]["actions"] == "accept"){
                row_class = "warning";
                status = '<button class=\"btn btn-danger btn-circle\" type=\"button\" flow_id="'+json_file[i]["id"]+'" onclick="deleteFlow($(this));"><b>X</b><i class=\"fa\"></i></button>'
            }
            else if(json_file[i]["actions"] == "drop"){
                row_class = "danger";
                status = '<button class=\"btn btn-danger btn-circle\" type=\"button\" flow_id="'+json_file[i]["id"]+'" onclick="deleteFlow($(this));"><b>X</b><i class=\"fa\"></i></button>'
            }
            else{
                row_class = "success";
                status = "<button class=\"btn btn-success btn-circle\" type=\"button\"><i class=\"fa fa-share\"></i></button>"
            }

            var tr = "<tr class=\""+ row_class +"\">" +
                        "<td>" + replaceIfNull(json_file[i]["priority"], "-") + "</td>" +
                        "<td>" + replaceIfNull(json_file[i]["protocol"], "-") + "</td>" +
                        "<td>" + replaceIfNull(json_file[i]["ip_src"], "-") + "</td>" +
                        "<td>" + replaceIfNull(json_file[i]["ip_dst"], "-") + "</td>" +
                        "<td>" + replaceIfNull(json_file[i]["port_src"], "-") + "</td>" +
                        "<td>" + replaceIfNull(json_file[i]["port_dst"], "-") + "</td>" +
                        "<td>" + replaceIfNull(json_file[i]["rate_limit"], "-") + "</td>" +
                        "<td>" + replaceIfNull(actionsHandler(json_file[i]["actions"]), "-") + "</td>" +
                        "<td>" + status + "</td>" +
                     "</tr>";

            $(".table_body").append(tr);

        }

    });
}

function deleteFlow(thisButton){
    // console.log(thisButton);
    deleteFlowAjax(function(data){
        // console.log(data);
    }, thisButton)
}

var interval = 2000;
printFlows();

setInterval(function(){
    printFlows()
}, interval);
