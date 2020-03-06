function autoSizeTextarea(){
  const target = $('textarea, .comment-reply-form-wrapper .comment-text');
  const defaultHeight = target.scrollHeight;

  target.on('input', autosize);

  function autosize(){
    var el = this;
    setTimeout(function(){
      el.style.cssText = `height:${defaultHeight}`;
      // for box-sizing other than "content-box" use:
      // el.style.cssText = '-moz-box-sizing:content-box';
      el.style.cssText = 'height:' + el.scrollHeight + 'px';
    },0);
  }
}

class InfiniteScroll{
  constructor(path, wrapperId, lastPage){
    if(path === undefined || wrapperId === undefined) throw Error('no parameter');
    this.path = path;
    this.pNum = 2;
    this.wNode = document.querySelector(`.${wrapperId}`);
    this.wrapperId = wrapperId;
    this.lastPage = lastPage;
    this.enable = true;

    this.detectScroll();
  }

  detectScroll(){
    const self = this;

    window.onscroll = (ev) => {
      let scrollHeight = Math.max(
        document.body.scrollHeight, document.documentElement.scrollHeight,
        document.body.offsetHeight, document.documentElement.offsetHeight,
        document.body.clientHeight, document.documentElement.clientHeight
      );
      let curScrollHeight = window.innerHeight + window.pageYOffset;
      if(curScrollHeight >= scrollHeight && self.pNum <= self.lastPage)
        self.getNewPost();
    }
  }

  getNewPost(){
    if(this.enable === false) return false;
    //스크롤 ajax 요청 중에는 사용 x
    self = this;
    this.enable = false;
    const xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = (ev) => {
        if(xmlhttp.readyState == XMLHttpRequest.DONE){
          if(xmlhttp.status == 200){
            self.pNum++;
            const childItems = this.getChildItemsByAjaxHTML(xmlhttp.responseText);
            this.appendNewItems(childItems);
          }
        }
        return this.enable = true;
    }
    xmlhttp.open('GET', `${location.origin + self.path + self.pNum}`, true);
    xmlhttp.send();
  }

  getChildItemsByAjaxHTML(HTMLText){
    const newHTML = document.createElement('html');
    newHTML.innerHTML = HTMLText;
    const childItems = newHTML.querySelectorAll(`.comment-item-wrapper`);
    return childItems;
  }

  appendNewItems(items){
    items.forEach(item => {
      this.wNode.appendChild(item);
    });
  }
}
