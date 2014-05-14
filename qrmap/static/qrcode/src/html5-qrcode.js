(function( $ ){

  $.fn.html5_qrcode = function(qrcodeSuccess, qrcodeError, videoError) {
    'use strict';
    
    var height = this.height();
    var width = this.width();
    
    if (height == null) {
      height = 250;
    }
    
    if (width == null) {
      width = 300;
    }
    
    var vidTag = '<video id="html5_qrcode_video" autobuffer controls width="' + width + 'px" height="' + height + 'px"></video>'
    var canvasTag = '<canvas id="qr-canvas" width="' + (width - 2) + 'px" height="' + (height - 2) + 'px" style="display:none;"></canvas>' 
    
    this.append(vidTag);
    this.append(canvasTag);
        
    var localMediaStream;
    var qrcode;

    var video = document.getElementById('html5_qrcode_video');
    video.addEventListener('click',function(){
      video.play();
    },false);
    var canvas;
    var context; 
    
    $('#qr-canvas').each(function(index, element) {
      canvas = element;
      context = element.getContext('2d');   
    });
    
   
    
    var scan = function() {
      if (localMediaStream) {
        context.drawImage(video, 0, 0, 307,250);
        console.log(localMediaStream);
        try {
          qrcode.decode();
        } catch(e) {
          qrcodeError(e);
        }

        setTimeout(scan, 500);

      } else {
        setTimeout(svan,500);
      }
    }//end snapshot function
    
    window.URL = window.URL || window.webkitURL || window.mozURL || window.msURL;
    navigator.getUserMedia  = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;

    var successCallback = function(stream) {
        video.src = (window.URL && window.URL.createObjectURL(stream)) || stream;
        localMediaStream = stream;

        video.play();
        setTimeout(scan,1000);
    }

    // Call the getUserMedia method with our callback functions
    if (navigator.getUserMedia) {
        navigator.getUserMedia({video: true}, successCallback, videoError);
    } else {
        console.log('Native web camera streaming (getUserMedia) not supported in this browser.');
        // Display a friendly "sorry" message to the user
    }

    qrcode.callback = qrcodeSuccess;

  }; // end of html5_qrcode
})( jQuery );