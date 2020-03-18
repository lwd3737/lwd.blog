window.onload = ev => {
  console.log('load');
  //tag 검색 or 추가
  $('#form-tag-btn').on('click', ev => {
    ev.preventDefault();

    const url = 'http://' + location.host + '/blog/tag/search/';
    const tagInput = $('.form-tags').find('input[name="tag_name"]');
    const tagName = $.trim(tagInput.val());
    const articleId = location.pathname.split('/')[2];

    //tag 값 validation
    if(tagName.length < 2){
      alert('2자 이상 입력해주세요.');
      return false;
    }

    tagInput.val('');

    $.ajax({
      url: url,
      data: {
        'tag_name': tagName,
      },
      dataType: 'json'
    })
    .done((data) => { //data: {tag_list:[{tag_id:tag_name}...]}
      let tag = data['tag'];
      const related_tags = data['related_tags'];
      console.log('tag, related_tags:',tag, related_tags);

      $('.tag-list').html('');

      if(tag || related_tags.length > 0){
        $('.tag-list').addClass('box-ui');

        if(tag){
          let tagEl = $(`<li class="tag-item" data-id="${tag['tag_id']}">
              ${tag['tag_name']}(${tag['count']})
            </li>`);

          $('.tag-list').append(tagEl);
        }
        else{
          let tagEl = $(`<li class="tag-item" data-id="">
              ${tagName}(0)
            </li>`);

          $('.tag-list').append(tagEl);
        }

        related_tags.forEach((tag, i) => {
          let tagEl = $(`<li class="tag-item" data-id="${tag['tag_id']}">
          ${tag['tag_name']}(${tag['count']})
          </li>`);

          $('.tag-list').append(tagEl);
        });
      }
      else{ //기존에 tag가 존재하지 않는다면 새로 추가
        //이미 추가된 태그라면 추가 x
        const addedTags = $('.added-tag');
        for(let i=0; i<addedTags.length; i++){
          const addedTagName = $.trim($('.added-tag')[i].innerHTML.split('<')[0]);
          if(tagName == addedTagName){
            alert('이미 추가된 태그입니다.');
            $('.tag-list').children().remove();
            return false;
          }
        }

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
  $('.tag-list').on('click', tagSelectEvent);

  function tagSelectEvent(ev){
    if(ev.target.className === 'tag-item'){
      const tagItem = $(ev.target);
      const tagId = tagItem.data('id');
      const tagName = $.trim(tagItem.text().split('(')[0]);

      //이미 추가된 태그라면 추가 x
      const addedTags = $('.added-tag');
      for(let i=0; i<addedTags.length; i++){
        const addedTagName = $.trim($('.added-tag')[i].innerHTML.split('<')[0]);
        if(tagName === addedTagName){
          alert('이미 추가된 태그입니다.');
          $('.tag-list').children().remove();
          return false;
        }
      }

      const addedTag = $(`<span class="added-tag" data-id="${tagId}">
        ${tagName} <span class="tag-cancel">&#10006;</span>
      </span>`);

      $('.added-tags').append(addedTag);
      $('.tag-list').removeClass('box-ui')
                    .find('.tag-item').remove();
    }
  }

  $('.added-tags').on('click', tagCancelEvent);

  function tagCancelEvent(ev){
    if(ev.target.className === 'tag-cancel'){
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

    let token = data['csrfmiddlewaretoken'];

    delete data['csrfmiddlewaretoken'];
    delete data['tag_name'];

    data['tags'] = [];
    for(let i=0; i<addedTags.length; i++){
      const name = $.trim(addedTags[i].textContent).split(' ')[0];
      const tagData = {id: addedTags[i].dataset['id'], name:name};
      data['tags'].push(tagData);
    }

    console.log(data);
    if(curTarget.id === 'public')
      data['is_public'] = 'true';
    else if(curTarget.id === 'save')
      data['is_public'] = 'false';

    $.ajax({
      url: url,
      headers: {'X-CSRFToken':token},
      data:JSON.stringify(data),
      type: 'POST',
    })
    .done(url =>{
      console.log(url);
      location.href = 'http://' + location.host + '/blog/my_articles/';
    })
    .fail((jqXHR, textStatus) => {
      alert(textStatus);
    });
  });

  //저장된 tag 불러오기

}
