"use strict";

const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}

function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

function sendData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

function renderCreateUserForm(body) {
    let ctrl = body["@controls"]["fpoint:add-user"]
    let form = $("<form>");
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitUser);
    Object.entries(ctrl.schema.properties).forEach(
        ([name, data]) => {
            form.append("<label>" + name + " ("+ data.description + " )</label>");
            form.append("<input type='text' name='" + name + "'>");
        }
    );
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function submitUser(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.name = $("input[name='name']").val();
    data.userName = $("input[name='userName']").val();
    //replace with your function
    //sendData(form.attr("action"), form.attr("method"), data, getSubmittedSensor);
}

function renderCreateUser(body) {
    $("div.navigation").html(
        "<a href='http://localhost:5000/api/' onClick='followLink(event, this, renderStartPage)'>Back</a>"
    );
    $(".contenttitle").html("<h1>Create a new user</h1>");
    $(".contentdata").empty();
    renderCreateUserForm(body);
}

function findUser(event) {
    event.preventDefault();
    let userName = $("input[name='userName']").val();
    let form = $("div.form form");
    //construct url to that user
    let url = form.attr("action")+userName+"/";
    getResource(url, renderUserPage);
}

function renderUserPage(body) {
    $("div.navigation").empty();
    $(".contenttitle").html("<h1>"+body.name+"</h1>");
    $(".contentdata").html("<p>Below is your collections:</p>");

    getResource(body["@controls"]["fpoint:collections-by"].href, renderCollections);
}

function renderCollections(body) {
    $(".resulttable thead").html(
        "<tr><th>Collection Name</th>><th>Actions</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        let link = "<a href='" +
                    item["@controls"].self.href +
                    "' onClick='followLink(event, this, renderCollection)'>show</a>";
        tbody.append("<tr><td>" + item.name +
            "</td><td>" + link + "</td></tr>"
        );
    });
}

function renderCollection(body) {
    //TODO: implement
}

function renderStartPage(body) {
    $("div.navigation").empty();
    $(".contenttitle").html("<h1>Welcome</h1>");
    $(".contentdata").html("<p>Enter your username, or <a href='" +
    body["@controls"]["fpoint:all-users"].href +
    "' onClick='followLink(event, this, renderCreateUser)'>create a new user.</a></p>");

    //form for login
    let form = $("<form>");
    form.attr("action", body["@controls"]["fpoint:all-users"].href);
    form.append("<label>Enter username</label>");
    form.append("<input type='text' name='userName'>");
    form.append("<input type='submit' class='submitbutton' name='submit' value='Enter'>");
    form.submit(findUser);
    $("div.form").html(form);
}

$(document).ready(function () {
    getResource("http://localhost:5000/api/", renderStartPage);
});
