use iotdata
echo criar indice TTL para alarmes
db.alarmes.createIndex( {"createdAt": 1}, {expireAfterSeconds: 3600} )