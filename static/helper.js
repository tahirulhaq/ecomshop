$(document).on("submit","#remove-order",function(event){
  event.preventDefault();
//   console.log("entered in decrement")
  $.ajax({
    type:'POST',
url:"{% url 'deleteOrder' order.id%}",
data:{
    order:$('#remove-order').val(),
    csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
    action: 'post',
    success: function(data){
        $("#orderTable #user-" + order).remove();
    }}
});
});
