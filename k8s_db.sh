service_name=$1
context=$2
if [[ ! $context ]]; then
  echo "Must provide args for service and env, e.g. './k8s_db.sh reachard-iii-web int1'"
  exit 1
fi
echo "Logging into DB for $service_name on $context"
kubectl config use-context $context
conn_info=`db_info.sh $service_name | awk '/DB_USER[NAME]*=|DB_PASS[WORD]*=|DB_HOST=|DB_NAME=/'`
arr=($(echo ${conn_info}))
for s in "${arr[@]}"
do
   :
  if [[ $s =~ "PASS" ]]; then
    pass=$(cut -d'=' -f2 <<< ${s})
  fi
  if [[ $s =~ "USER" ]]; then
    user=$(cut -d'=' -f2 <<< ${s})
  fi
  if [[ $s =~ "HOST" ]]; then
    host=$(cut -d'=' -f2 <<< ${s})
  fi
  if [[ $s =~ "DB_NAME" ]]; then
    db_name=$(cut -d'=' -f2 <<< ${s})
  fi
done

psql postgres://$user:$pass@$host:5432/$db_name
