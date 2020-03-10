window.onload = ev => {
  console.log('load');
  //tag 검색 or 추가
  $('#form-tag-btn').on('click', ev => {
    ev.preventDefault();

    const url = 'http://' + location.host + '/blog/tag/search/';
    const tagInput = $('.form-tags').find('input[name="tag_name"]');
    const tagName = $.trim(tagInput.val());

    //tag 값 validation
    if(tagName.length < 2){
      alert('2자 이상 입력해주세요.');
      return false;
    }

    tagInput.val('');

    $.ajax({
      url: url,
      data: {
        'tag_name': tagName
      },
      dataType: 'json'
    })
    .done((data) => { //data: {tag_list:[{tag_id:tag_name}...]}
      const tagList = data['tag_list'];

      if(tagList.length > 0){
        for(let tag in tagList){
          const tagId = Object.keys(tag)[0];
          let tagEl = $(`<li class="tag-item" data-id="${tagId}">${tag[tagId]}</li>`);

          $('.tag-list').append(tagEl);
        }
      }
      else{ //기존에 tag가 존재하지 않는다면 새로 추가
        const addedTag = $(`<span class="added-tag" data-id="">
          ${tagName} <span class="tag-cancel">&#10006;</span>
        </span>`);

        $('.added-tags').append(addedTag);
      }
    })
    .fail((jqXHR, textStatus) => {
      alert(textStatus);
    });
  });

  //tag 검색 성공시 태크 목록에 추가
  $('.added-tags').on('click', tagEvent);

  function tagEvent(ev){
    if(ev.target.className === 'tag-item'){
      const tagItem = $(ev.target);
      const tagId = tagItem.data('id');
      const tagName = $.trim(tagItem.text());
      const addedTag = $(`<span class="added-tag" data-id="${tagId}">
        ${tagName} <span class="tag-cancel">&#10006;</span>
      </span>`);

      $('.added-tags').append(addedTag);
    }
    else if(ev.target.className === 'tag-cancel'){
      const addedTag = ev.target.parentNode;

      if(addedTag)
        addedTag.remove();
    }
  }

  $('#article-form-btn button').on('click', ev => {
    ev.preventDefault();

    let serializedData = $('.article-form').serializeArray();
    let data = {};
    let path = location.pathname.split('/');
    let url = 'http://' + location.host;
    const addedTags = $('.added-tag');
    const curTarget = ev.currentTarget;

    for(let i=0; i<path.length; i++){
      if(path[i] == 'new'){
        url += '/blog/article/new/';
        break;
      }
      if(path[i] == 'edit'){
        url += `/blog/detail/${path[3]}/edit/`;
        break;
      }
    }

    for(let i=0; i<serializedData.length; i++){
      data[serializedData[i]['name']] = serializedData[i]['value'];
    }

    delete data['tag_name'];

    data['tags'] = [];
    for(let i=0; i<addedTags.length; i++){
      const name = $.trim(addedTags[0].textContent).split(' ')[0];
      const tagData = {id: addedTags[i].dataset['id'], name:name};
      data['tags'].push(tagData);
    }

    console.log('btn id:', curTarget.id);
    if(curTarget.id === 'public')
      data['is_public'] = 'true';
    else if(curTarget.id === 'save')
      data['is_public'] = 'false';

    $.post({
      url: url,
      data: data
    })
    .done(url =>{
      console.log(url);
      location.href = 'http://' + location.host + '/blog/my_articles/';
    })
    .fail((jqXHR, textStatus) => {
      alert(textStatus);
    });
  });
}
