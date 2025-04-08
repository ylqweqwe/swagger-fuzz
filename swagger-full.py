import json
import time
import requests
import csv,numpy.compat.setup
 


def get_specs(url):
    specs_url = url + "/swagger-resources"
    res = requests.get(url = specs_url)
    specs = json.loads(res.text)

    return specs

def check_spec(spec_url,url,f):
    res = requests.get(url = spec_url)
    try:
        paths = json.loads(res.text)['paths']
        print("[+] : 此标准下共有 %d 个接口"%(len(paths)))
    except:
        print("此标准为空")
        return 0

    for path in paths:
        print("[+] : 开始测试接口 %s " %(path))
        methods = paths[path]
        for method in methods:

            tags = paths[path][method]['tags'][0]
            summary = paths[path][method]['summary']

            operationId = paths[path][method]['operationId']
            if 'consumes' in paths[path][method].keys():
                consumes = paths[path][method]['consumes'][0]
            else:
                consumes = '0'
                
            if consumes != '0':

                json_string = '''{
  "contractNumber": "string",
  "createdBy": "string",
  "createdTime": "2021-02-01T09:33:58.398Z",
  "cutoffDate": "2021-02-01T09:33:58.398Z",
  "delFlag": "string",
  "dispatchForm": "string",
  "dispatchUnit": "string",
  "effectDate": "2021-02-01T09:33:58.398Z",
  "fileList": "string",
  "id": 0,
  "makeDate": "2021-02-01T09:33:58.398Z",
  "manageMethod": "string",
  "name": "string",
  "peopleNumber": "string",
  "remark": "string",
  "title": "string",
  "updatedBy": "string",
  "updatedTime": "2021-02-01T09:33:58.398Z"
}'''


                if method == "post":
                    res = requests.post(url = url + path , data = json_string)
                elif method == "put":
                    res = requests.put(url = url + path , data = json_string)

                try:
                    row = [spec_url,summary,path,method,consumes,url + path,str(len(paths[path][method]['parameters'])),json_string,res.status_code,res.text]
                except:
                    row = [spec_url,summary,path,method,consumes,url + path,'0',json_string,res.status_code,res.text]
                writer.writerow(row)
                

            else:
                if "{" in path:

                    parameter = paths[path][method]['parameters'][0]
                    try:
                        if parameter['type'] == "boolean":
                            tmp = "true"
                        else:
                            tmp = "1"
                    except:

                        tmp = "{1}"
                    if method == 'get':
                        res = requests.get(url = url + path[:path.index('{')] + tmp)

                    elif method == 'delete':
                        res = requests.delete(url = url + path[:path.index('{')] + tmp)

                    row = [spec_url,summary,path,method,consumes,url + path[:path.index('{')],str(len(paths[path][method]['parameters'])),"",res.status_code,res.text]
                    writer.writerow(row)

                else:
                    query_string = ''
                    if 'parameters' in paths[path][method]:
                        parameters = paths[path][method]['parameters']
                        num_of_param = len(parameters)

                        for parameter in parameters:

                            try:
                                if parameter['type'] == "boolean":
                                    query_string += "&%s=true"%(parameter['name'])
                                else:
                                    query_string += "&%s=1"%(parameter['name'])
                            except:

                                query_string += "&%s={1}"%(parameter['name'])
                    else:
                        query_string = ''
                        num_of_param = 0

                    query_string = query_string[1:]


                    if method == "get":
                        res = requests.get(url = url + path + "?" + query_string)

                    elif method == "delete":
                        res = requests.delete(url = url + path + "?" + query_string)


                    row = [spec_url,summary,path,method,consumes,url + path + "?" + query_string,str(num_of_param),"",res.status_code,res.text]
                    writer.writerow(row)



        time.sleep(0)


if __name__ == '__main__':
    url = ""
    specs = get_specs(url)
    print("第 %d 个接口"%(len(specs)))

    f = open('swagger.csv','w',newline='',encoding='utf-8')
    writer = csv.writer(f)
    try:
        writer.writerow(["接口","summary","path","method","consumes","url","num of params","data","status_code","response"])
    except Exception as e:
        print(e)

    for spec in specs:
        spec_url = url + spec['url']
        pre = spec['url'].split('/')[1]
        print("%s 接口"%(spec_url))
        check_spec(spec_url,url + "/" + pre,f)

