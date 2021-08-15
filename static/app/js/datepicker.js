$(function() {
  'use strict';

  if($('#datePickerStart').length) {
    var date = new Date();
    var today = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    $('#datePickerStart').datepicker({
      format: "mm-dd-yyyy",
      todayHighlight: true,
      autoclose: true
    });
    // $('#datePickerStart').datepicker('setDate', today);
  }
  if($('#datePickerEnd').length) {
    var date = new Date();
    var today = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    $('#datePickerEnd').datepicker({
      format: "mm-dd-yyyy",
      todayHighlight: true,
      autoclose: true
    });
    // $('#datePickerEnd').datepicker('setDate', today);
  }
});
