
export default class ContentsListAPI {
  call(success, failed, page) {
    if(page) {
      fetch(`/api/contents/?format=json&page=${page}`)
        .then(res => {
          return res.json();
        })
        .then(success)
        .catch(failed);
    } else {
      fetch('/api/contents/?format=json')
      .then(res => res.json())
      .then(success)
      .catch(failed);
    }
  }
};
