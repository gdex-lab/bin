# pass in name of service for k8s to search pods
service_name=$1
# get pod info
pod_info=$(kubectl get pods | grep $service_name)
# extract name of first pod listed for the service
pod_name=`echo $pod_info | awk '{print $1;}'`
# grep entrypoint for DB information
kubectl exec $pod_name ./entrypoint.sh env | grep DB;
