# lookup service creation
from flask import Flask
from flask_restful import Resource, Api
from sqlalchemy import create_engine

# As given in the task provided the prefix
API_PREFIX = 'urlinfo/1'

#Fetch information from database
info = create_engine('sqlite:///service.db)

app = Flask(__name__)
api = Api(app)


class NewUrl(Resource):
    def sql_query(sql='', params=''):
        if sql:
            query = None
            try:
                connection = info.connect()

                if params:
                    query = connection.execute(sql, params)
                else:
                    query = connection.execute(sql)

                return query.cursor.fetchall()
            finally:
                if query:
                    query.cursor.close()
        else:
            pass

    def get(self, path):
        global API_PREFIX
        api_path = [API_PREFIX, API_PREFIX + '/']
        result = {'error': False}
        sql = []
        url = path.split('/')
        if path in api_path:
            # Include malware lists
            sql.append("select domain, uri from malware")
        elif path.startswith(API_PREFIX):
            try:
                host, uri = url[2], '/' + '/'.join(url[3:])
            except IndexError:
                host, uri = url[2], '/'
            sql.append("select domain, uri, result from malware "
                       "where domain=(:host) and uri=(:uri)")
            sql.append((host, uri,))
        else:
            result['error'] = True
            result['message'] = 'bad requst'
            return result, 400

        output = self.sql_query(*sql)

        if path in api_path:
            result['urls'] = [i[0] + i[1] for i in output]
        else:
            try:
                result['url'] = output[0][0] + output[0][1]
                result['status'] = output[0][2]
            except IndexError as e:
                result['url'] = host + uri
                result['status'] = 'OK'
                result['error'] = True
        return result, 200
api.add_resource(NewUrl, '/<path:path>')


if __name__ == '__main__':
    app.run()
