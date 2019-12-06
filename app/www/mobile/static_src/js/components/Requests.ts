// import {Promise} from "es6-promise";


interface IRequestsDict {
    url: string;
    method?: string;
    headers?: any;
    body?: any;
}

export class Requests {

    public static request(obj: IRequestsDict): Promise<any> {
        return new Promise((resolve: any, reject: any) => {
            let xhr = new XMLHttpRequest();
            xhr.open(obj.method || 'GET', obj.url);
            if (obj.headers) {
                Object.keys(obj.headers).forEach(key => {
                    xhr.setRequestHeader(key, obj.headers[key]);
                });
            }
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(xhr.response);
                } else {
                    reject(xhr.statusText);
                }
            };
            xhr.onerror = () => reject(xhr.statusText);
            xhr.send(obj.body);
        });
    }

    public static requestJSON(obj: IRequestsDict): Promise<any> {
        if (!obj.hasOwnProperty('headers')) {
            obj['headers'] = {};
        }
        obj['headers']['Content-Type'] = 'application/json';
        return Requests.request(obj);
    }

}
