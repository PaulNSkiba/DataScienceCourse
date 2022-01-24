var HOST = "http://localhost:5000/"
//document.location.href = "/";
//alert('changeurl')

if (history.pushState) {
    window.history.pushState("", "Title", "/");
  } else {
    document.location.href = "/";
  }
