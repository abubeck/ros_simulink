

import org.apache.xmlrpc.common.TypeConverterFactoryImpl;
import org.apache.xmlrpc.server.PropertyHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcServer;
import org.apache.xmlrpc.server.XmlRpcServerConfigImpl;
import org.apache.xmlrpc.server.RequestProcessorFactoryFactory;
import org.apache.xmlrpc.webserver.WebServer;
import org.apache.xmlrpc.*;

public class MatlabRequestProcessorFactoryFactory implements
      RequestProcessorFactoryFactory {
    private final RequestProcessorFactory factory =
      new MatlabRequestProcessorFactory();
    private final matlabinterface matlab;

    public MatlabRequestProcessorFactoryFactory( matlabinterface matlab) {
      this.matlab = matlab;
    }

    public RequestProcessorFactory getRequestProcessorFactory(Class aClass)
         throws XmlRpcException {
      return factory;
    }

    private class MatlabRequestProcessorFactory implements RequestProcessorFactory {
      public Object getRequestProcessor(XmlRpcRequest xmlRpcRequest)
          throws XmlRpcException {
        return matlab;
      }
    }

}


