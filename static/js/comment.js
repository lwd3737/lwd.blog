function commentToggle(){
    const toggle = $(this);
    const commentContainer = $('.comment-container');
    let loadFlag = toggle.data('load');
    let showFlag = toggle.data('show');

    if(!loadFlag){
      comment.commentLoad();
      toggle.data('load', true);
      commentContainer.on('load', ev => $('.reply-btn', '.comment-list').on('click', replyToggle));
    }
    if(showFlag){
      commentContainer.css('display', 'none');
      toggle.data('show', false);
    }
    else{
      commentContainer.css('display', 'block');
      toggle.data('show', 'true');
    }
}

function replyToggle(ev){
  const curTarget = ev.target;

  if(curTarget.classList.contains('reply-btn') === false || curTarget.closest('.comment-reply-item'))
    return;

  const replyWrapper = $(curTarget.closest('.comment-item')).siblings('.comment-reply-wrapper');
  const replyBtn = $(curTarget, '.comment-item');
  let showFlag = replyBtn.data('show');
  let replyCount = replyWrapper.find('.comment-reply-list').data('count');

  if(showFlag){
    replyWrapper.css('display', 'none');
    replyBtn.data('show', false).attr('data-show', false);
    if(replyCount === 0)
      replyBtn.text('댓글 작성');
    else
      replyBtn.text(`댓글 ${replyCount}개 보기`);
  }
  else{
    replyWrapper.css('display', 'block');
    replyBtn.data('show', true).attr('data-show', true)
            .text('댓글 접기');
  }
}

const comment = {
  commentLoad(){
    const commentContainer = $('.comment-container');
    const self = this;

    $.ajax({
      url:comment_url,
      dataType:'html',
      type:'GET',
    })
    .done(function(response){
      if(response.status == 'error'){
        alert('댓글 가져오기 실패 ' + response.statusCode);
      }

      commentContainer.append(response);

      //comment item들이 부모 자식 관계가 되는 버그 발생
      const commentItemWrappers = commentContainer.find('.comment-list .comment-item-wrapper');
      commentContainer.find('.comment-list').children().remove();
      commentContainer.find('.comment-list').append(commentItemWrappers);

      const form = $('#comment-form form');

      //comment 생성
      if(form.hasClass('authenticated-form')){

        const authenticatedFormLoad = (() => {
          const url = `comment/new/`;

          form.on('submit', function commentNew(ev){
            ev.preventDefault();

            const text = form.find('.comment-text textarea').val();

            $.ajax({
              url: url,
              headers: {'X-CSRFToken': token},
              data:{
                'text': text,
              },
              method:'POST'
            })
            .done(function(data){
              //form 빈 값으로 만들기
              form.find('textarea').val('');

              //생성된 댓글 삽입하기
              const insertCommentToCommentList = (() => {
                const commentItemWrapper = $('.comment-item-wrapper', '.comment-layer').clone();

                const commentItem = commentItemWrapper.find('.comment-item');
                commentItem.find('.user-profile').text(data['user']);
                commentItem.find('.comment-text').text(data['text']);
                commentItem.find('.last-modified-time').text(data['created_time']);

                const replyWrapper = commentItemWrapper.find('.comment-reply-wrapper');

                const replyForm = replyWrapper.find('form');
                replyForm.find('.user-profile').text(data['user']);

                $('.comment-list').prepend(commentItemWrapper);
                commentItemWrapper.attr('data-comment-id', data['comment_id']);

                const commentToggle = $('.comment-toggle');
                const commentCount = parseInt(commentToggle.attr('data-count')) + 1;
                commentToggle.attr('data-count', commentCount)
                             .text(`댓글 ${commentCount}개`);

                replyForm.find('.comment-text').html('');

                scrollTo(commentItemWrapper.get(0));
              })();
            })
            .fail(function(jqXHR, textStatus){
              alert('댓글 달기 실패:', textStatus);
            });
          });
        })();
      }

      else{

        const nonAuthenticatedFormLoad = (() => {
          form.parent().css('background', 'rgb(235, 235, 228)')
          .find('textarea').css('color', 'gray');

          //로그인 폼으로 리다이렉션
        })();
      }

      //각 comment에 대한 reply들을 불러오기
      commentReply.replyLoad();

      autoSizeTextarea();

      const makeReplyToggle = (() => {
        const commentList = $('.comment-list');
        const replyBtn = $('.reply-btn');
        commentList.on('click', replyBtn, replyToggle);
      })();

      const makeOptions = (() => {
        const commentList = $('.comment-list');
        const targetSelector = '.comment-item .option';
        commentList.on('click', targetSelector, self.optionEvent);
      })();

      self.infiniteScroll();
    });
  },

  optionEvent(ev){
    const curTarget = ev.target;
    const articleId = location.pathname.split('/')[3];
    let commentId = curTarget.closest('.comment-item-wrapper').dataset['commentId']
    let url;

    //comment-reply에서 삭제를 했다면
    if($(curTarget).parents('.comment-reply-item').length > 0)
      return;

    if(curTarget.id === 'edit'){

      const editAction = (() => {
          const commentItemWrapper = $(`.comment-item-wrapper[data-comment-id="${commentId}"]`);
          const commentLayer = $('.comment-layer');

          url = `comment/${commentId}/edit/`;

          const changeToEditForm = (() => {
            const commentItem = commentItemWrapper.find('.comment-item');
            const commentText = $.trim(commentItem.find('.comment-text').text());

            const commentFormWrapper = commentLayer.find('.comment-form-wrapper').clone();

            commentFormWrapper.addClass('edit-form')
                              .find('.comment-text textarea').val(commentText);

            commentItem.remove();

            commentItemWrapper.prepend(commentFormWrapper);

            commentFormWrapper.on('submit', commentEdit);

          })();

          function commentEdit(ev){
            ev.preventDefault();

            const commentText = commentItemWrapper.find('.comment-text textarea').val();

            const sendData = {
              'text':commentText,
            };

            $.ajax({
              url:url,
              headers: {'X-CSRFToken': token},
              method:'POST',
              data: sendData,
            })
            .done(function (data){

              if(data['fail']){
                alert(data['fail']);
                return;
              }

              const changeToCommentItem = (() => {

                const commentItem = commentLayer.find('.comment-item').clone();
                commentItem.find('.user-profile').text(data['user']);
                commentItem.find('.comment-text').text(data['text']);
                commentItem.find('.last-modified-time').text(data['updated_time']);

                const commentFormWrapper = commentItemWrapper.find('.comment-form-wrapper');
                commentFormWrapper.remove();

                commentItemWrapper.prepend(commentItem);
              })();

            })
            .fail(function (jqXHR, textStatus){

              alert('댓글 수정 실패:', textStatus);

            });
          }
      })();
    }
    else if(curTarget.id === 'delete'){

      if(confirm('정말 삭제하시곘습니까?') === true){

        const deleteAction = (() => {
          url = `comment/${commentId}/delete/`;

          $.ajax({
            url:url,
            headers: {'X-CSRFToken': token},
            method: 'POST',
          })
          .done(data => {
            commentId = data['comment_id'];
            const comment = $(`.comment-item-wrapper[data-comment-id="${commentId}"]`);
            comment.next('.comment-between').remove();
            comment.remove();
          })
          .fail((jqXHR, textStatus) => {
            alert('댓글 삭제 실패:', textStatus);
          });
        })();
      }
      else{

          return;
      }
    }
  },

  infiniteScroll(){
    const commentListId = 'comment-list';
    const detailId = location.pathname.split('/')[3];
    const paginatePath = `/blog/detail/${detailId}/comments_display?page=`;
    const lastPage = $('.comment-list').data('last-page');
    const infiniteScroll = new InfiniteScroll(paginatePath, commentListId, lastPage);
  }
};

const commentReply = {
  replyLoad(){

    const self = this;
    const form = $('.comment-reply-form-wrapper form');

    if(form.hasClass('authenticated-form')){

      const authenticatedFormLoad = (() => {
        $('.comment-list').on('submit', function(ev){
          ev.preventDefault();

          const target = ev.target
          const replyFormWrapper = target.closest('.comment-reply-form-wrapper');
          //comment-reply-form-wrapper edit-form 내부에서 발생한 이벤트가 아니라면

          if(!replyFormWrapper || replyFormWrapper.classList.contains('edit-form'))
            return;

          const commentItemWrapper = $(target).parents('.comment-item-wrapper');
          const commentId = commentItemWrapper.attr('data-comment-id');
          const commentText = $(target).find('.comment-text');

          const _data = (() => {
            let targetUser;
            let targetReplyId;
            let content;
            let text;

            if(targetUser = commentText.find('.target-user')[0]){
              targetReplyId = targetUser.dataset['targetReplyId'];

              targetUser.remove();
              text = commentText.html();
            }
            else{
              targetReplyId = null;
              text = commentText.html();
            }

            return {text:text, targetReplyId:targetReplyId};
          })();

          const url = location.pathname + `comment/${commentId}/reply/new/`;

          $.ajax({
            url: url,
            headers: {'X-CSRFToken': token},
            data:{
              'text': _data['text'],
              'target_reply_id':_data['targetReplyId'],
            },
            method: 'POST',
          })
          .done(function(data){

            const insertReplyToReplyList = (() => {
              const replyList = $(`.comment-item-wrapper[data-comment-id="${data['comment_id']}"]`)
                .find('.comment-reply-list');

              form.find().val('');

              const replyItem = $('.comment-reply-item', '.comment-layer').clone();
              replyItem.attr('data-reply-id', data['reply_id']);
              replyItem.find('.user-profile').text(data['user']);
              replyItem.find('.last-modified-time').text(data['created_time']);

              let targetUser;
              if(data[['target_reply_id']]){
                targetUser = `<span class="target-user" contenteditable="false"
                  data-target-reply-id="${data['target_reply_id']}">${data['target_user_name']}</span>`;
              }
              const contentHtml = targetUser ? targetUser + ' ' + data['text'] : data['text'];
              replyItem.find('.comment-text').html(contentHtml);

              replyList.append(replyItem);
              commentText.html('');

              //댓글 갯수 추가
              const addCommentCount = (() => {
                const commentToggle = $('.comment-toggle');
                const commentCount = parseInt(commentToggle.attr('data-count')) + 1;
                commentToggle.attr('data-count', commentCount)
                .text(`댓글 ${commentCount}개`);
              })();

              //대댓글 갯수 추가
              const addReplyCount = (() => {
                const replyCount = parseInt(replyList.attr('data-count')) + 1;
                replyList.attr('datat-count', replyCount);
              })();

              scrollTo(replyItem[0]);
            })();
          })
          .fail(function(jqXHR, textStatus){
            alert("댓글 달기 실패:", textStatus);
          });
        });
      })();

      const makeOptions = (() => {
        const commentList = $('.comment-list');
        const targetSelector = '.comment-reply-item .option';
        commentList.on('click', targetSelector, self.optionEvent);
      })();

      const addReplyToReplyEvent = (() => {
        const selector = '.comment-reply-list .reply-btn';
        const commentList = $('.comment-list');
        commentList.on('click', selector, self.replyToReply);
      })();
    }
    else{

      const nonAuthenticatedFormLoad = (() => {
        form.parent().css('background', 'rgb(235, 235, 228)');
      })();
    }

  },

  optionEvent(ev){
    const curTarget = ev.target;
    const commentItemWrapper = curTarget.closest('.comment-item-wrapper');
    const replyItem = curTarget.closest('.comment-reply-item');
    let articleId = location.pathname.split('/')[3];
    let commentId = commentItemWrapper.dataset['commentId'];
    let replyId = replyItem.dataset['replyId'];
    let url;

    //comment에서 삭제 요청을 했다면
    if($(curTarget).parents('.comment-item').length > 0)
    return;

    if(curTarget.id === 'edit'){
      const editAction = (() => {
          const commentReplyWrapper = curTarget.closest('.comment-reply-wrapper');
          const commentLayer = $('.comment-layer');
          let targetUser;
          let targetUserStr;
          let replyText = '';

          url = `comment/${commentId}/reply/${replyId}/edit/`;

          const changeToEditForm = (() => {
            const commentText = replyItem.querySelector('.comment-text');
            targetUser = commentText.querySelector('.target-user');

            if(targetUser){
              targetUserStr = `<span class="target-user" contenteditable="false"
              data-target-reply-id="${targetUser.dataset['targetReplyId']}">
              @${targetUser.textContent}</span>`;
              replyText += targetUserStr + ' ';
              targetUser.remove();
            }

            replyText += $.trim(commentText.innerHTML);
            const replyList = curTarget.closest('.comment-reply-list');
            const replyFormWrapper = commentLayer.find('.comment-reply-form-wrapper').clone();


            replyFormWrapper.addClass('edit-form')
                            .find('.comment-text').html(replyText)
                            .attr('contenteditable', 'true');

            $(replyItem).replaceWith(replyFormWrapper);

            replyFormWrapper.on('submit', replyEdit);

          })();

          function replyEdit(ev){
            ev.preventDefault();

            const curTarget = ev.currentTarget;
            const replyText = curTarget.querySelector('.comment-text').innerHTML;

            const sendData = {
              'text':replyText,
            };
            console.log(url);

            $.ajax({
              url:url,
              headers: {'X-CSRFToken': token},
              method:'POST',
              data: sendData,
            })
            .done(function (data){

              if(data['fail']){
                alert(data['fail']);
                return;
              }

              const changeToReplyItem = (() => {
                let contentHtml = '';

                //if(targetUser){
                //  contentHtml += targetUserStr;
                //}
                //contentHtml += data['text'];

                const replyItem = commentLayer.find('.comment-reply-item').clone();
                replyItem.find('.user-profile').text(data['user']);
                replyItem.find('.last-modified-time').text(data['updated_time']);
                replyItem.attr('data-reply-id', data['reply_id'])
                replyItem.find('.comment-text').html(replyText);

                const replyFormWrapper = $(commentItemWrapper).find('.comment-reply-list .edit-form');
                replyFormWrapper.replaceWith(replyItem);

              })();

            })
            .fail(function (jqXHR, textStatus){

              alert('댓글 수정 실패:', textStatus);

            });
          }
      })();
    }
    else if(curTarget.id === 'delete'){

      if(confirm('정말 삭제하시곘습니까?') === true){

        const deleteAction = (() => {
          articleId = location.pathname.split('/')[3];
          commentId = curTarget.closest('.comment-item-wrapper').dataset['commentId'];
          replyId = curTarget.closest('.comment-reply-item').dataset['replyId'];
          url = `comment/${commentId}/reply/${replyId}/delete/`;

          $.ajax({
            url:url,
            headers: {'X-CSRFToken': token},
            method: 'POST',
          })
          .done(data => {
            commentId = data['comment_id'];
            const comment = $(`.comment-item-wrapper[data-comment-id="${commentId}"]`);
            const reply = comment.find(`.comment-reply-item[data-reply-id="${data['reply_id']}"]`);
            reply.remove();
          })
          .fail((jqXHR, textStatus) => {
            alert('댓글 삭제 실패:', textStatus);
          });
        })();
      }
      else{

          return;
      }
    }
  },

  replyToReply(ev){
    const target = ev.target;

    if(!target.classList.contains('reply-btn') && !target.closest('.comment-reply-list'))
      return;

    const user = $(target).siblings('.comment-header').find('.user-profile');
    const username = $.trim(user.text());
    const replyId = target.closest('.comment-reply-item').dataset['replyId'];
    const commentReplyWrapper = target.closest('.comment-reply-wrapper');
    const commentText = $(commentReplyWrapper).find('.authenticated-form .comment-text').not('.edit-form');
    const targetUserSel = `<span class="target-user">${username} </span>`;
    //자신의 대댓글에 댓글달 때(프로필에서 id값 얻기)

    //다른 사람의 대댓글에 댓글을 달 때

    commentText.focus();

    const setCursorAfterTargetUser = ((container, targetUserSel, replyId) => {
      const range = new Range();
      const sel = window.getSelection();
      let newEl = document.createElement('span');
      let content;
      let textNode;
      let targetUser;

      newEl.className = 'comment-text__content';
      newEl.appendChild(document.createTextNode(' '))

      //user label이 존재한다면 제거
      if(targetUser = container.querySelector('.target-user')){
        targetUser.remove();
      }

      container.innerHTML = '';

      targetUser = $(targetUserSel)[0];
      targetUser.contentEditable = false;
      //서버에서 user id 획득
      targetUser.dataset['targetReplyId'] = replyId;

      container.appendChild(targetUser);
      container.appendChild(newEl);

      range.setStartAfter(container.querySelector('.comment-text__content'), 1);
      range.collapse(true);

      newEl.remove();

      sel.removeAllRanges();
      sel.addRange(range);

    })(commentText[0], targetUserSel, replyId);

    scrollTo(commentText[0]);
  }
};

//utility
function scrollTo(el){
  const posY = el.getBoundingClientRect().top + window.scrollY -50;
  window.scroll({
    top:posY,
    behavior: 'smooth'
  });
}


$('.comment-toggle').on('click', commentToggle);
