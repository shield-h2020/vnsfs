$(".sidebar-item").on("click", function(){
    thisA = $(this);
//    console.log(thisA.attr('name'))

    if (thisA.attr('name') === "testing_environment"){

        $( "#page-wrapper" ).load( "/testing_environment", function() {
            // thisA.addClass('active');
            thisA.parent().siblings().removeClass('active');
            thisA.parent().siblings().find(".active").removeClass('active');
            thisA.parent().siblings().find(".in").removeClass('in');
        });
    }
    else if(thisA.attr('name') === "tests"){
        $( "#page-wrapper" ).load( "/tests", function() {
            // thisA.addClass('active');
            thisA.parent().siblings().removeClass('active');
            thisA.parent().siblings().find(".active").removeClass('active');
            thisA.parent().siblings().find(".in").removeClass('in');
            //console.log(thisA.parent().siblings().children(".sidebar-item")) //.removeClass('active');
        });
    }

});

$(".sidebar-item-level2").on("click", function(){
    thisA = $(this);
//    console.log(thisA.attr('name'));

    // Change page header
    $(".page-header").text(thisA.text());

    panel = $("div[sidebar-name-link="+thisA.attr('name')+"]");

    panel.parents("div[sidebar-name-link]").removeClass("hidden");

    // show matching panel
    panel.removeClass("hidden");
    // show matching panel's children
//    panel.children().find("div[sidebar-name-link]").removeClass("hidden");
    panel.find(".hidden").not(".alert ").removeClass("hidden");

    // Hide clicked, in-page title
    panel.children(".test-heading").addClass("hidden");
    //
    panel.children().children(".test-heading").addClass("hidden");




    // hide matching panel's siblings
//    panel.siblings().not(".test-heading").addClass("hidden");
    panel.siblings().addClass("hidden");
    // hide matching panel's parent siblings
//    panel.parents("div[sidebar-name-link]").siblings().not(".test-heading").addClass("hidden");
    panel.parents("div[sidebar-name-link]").siblings().addClass("hidden");

});

function showTestsTabIfPlatformIsInstalled(){
    checkTestingEnvironmentAjax(null, function(response){
        if (response["result"] === false || response["result"] === "false"){
            $(".sidebar-item[name='tests']").addClass("hidden");
        }
        else{
            $(".sidebar-item[name='tests']").removeClass("hidden");
        }
    });
}