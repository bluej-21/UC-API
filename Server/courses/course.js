/**
 * Created by J on 5/22/2016.
 */

export class Course {

  private _data;

  constructor(data) {
    this.data = JSON.parse(data);
  }

  get data() {
    return this._data;
  }

  set data(val) {
    this._data = val;
  }
}
  
