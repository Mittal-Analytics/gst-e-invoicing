/* global localStorage */
(function () {
  function getStoredArticles () {
    var allItems = localStorage.getItem('articles')
    return allItems.split(',')
  }

  function getArticleInNav (articleUrl) {
    var element = document.querySelector(`[data-article="${articleUrl}"]`)
    return element
  }

  function markAsReadInNav (articleUrl) {
    var element = getArticleInNav(articleUrl)
    if (element) {
      var icon = element.querySelector('i')
      icon.classList.remove('icon-circle-empty')
      icon.classList.add('icon-ok-circled')
    }
  }

  function getCurrentArticle () {
    var el = document.querySelector('article[data-current-article]')
    return el.getAttribute('data-current-article')
  }

  function isReadArticle (currentArticle) {
    var storedArticles = getStoredArticles()
    return storedArticles.indexOf(currentArticle) > -1
  }

  function markAsUnReadInNav (currentArticle) {
    var element = getArticleInNav(currentArticle)
    if (element) {
      var icon = element.querySelector('i')
      icon.classList.remove('icon-ok-circled')
      icon.classList.add('icon-circle-empty')
    }
  }

  function markAsUnreadInStorage (currentArticle) {
    var storedArticles = getStoredArticles()
    var newList = storedArticles.filter(function (articleUrl) {
      return articleUrl !== currentArticle
    })
    localStorage.setItem('articles', newList.join(','))
  }

  function markAsReadInStorage (currentArticle) {
    var storedArticles = getStoredArticles()
    storedArticles.push(currentArticle)
    localStorage.setItem('articles', storedArticles.join(','))
  }

  function loadReadMarkers () {
    if (localStorage.getItem('articles') === null) {
      localStorage.setItem('articles', '')
    }

    var currentArticle = getCurrentArticle()
    var button = document.getElementById('mark-read-toggle')

    var storedArticles = getStoredArticles()
    for (var i = 0; i < storedArticles.length; i++) {
      var articleUrl = storedArticles[i]
      markAsReadInNav(articleUrl)

      if (articleUrl === currentArticle && button) {
        button.innerText = 'Mark as unread'
      }
    }
  }

  function toggleRead (button) {
    var currentArticle = getCurrentArticle()

    if (isReadArticle(currentArticle)) {
      markAsUnReadInNav(currentArticle)
      markAsUnreadInStorage(currentArticle)
      button.innerText = 'Mark as read'
    } else {
      markAsReadInNav(currentArticle)
      markAsReadInStorage(currentArticle)
      button.innerText = 'Mark as unread'
    }
  }

  function setupEverything () {
    loadReadMarkers()
    window.toggleRead = toggleRead
  }

  setupEverything()
})()
