
export default class UserAPI {
  call(userId, success, failed) {
    fetch(`/api/users/${userId}?format=json`)
      .then(res => res.json())
      .then(success)
      .catch(failed);
  }
};
