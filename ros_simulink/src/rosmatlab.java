import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;

// Dependency --> libxmlrpc3-server-java
import java.net.InetAddress;

import org.apache.xmlrpc.common.TypeConverterFactoryImpl;
import org.apache.xmlrpc.server.PropertyHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcServer;
import org.apache.xmlrpc.server.XmlRpcServerConfigImpl;
import org.apache.xmlrpc.webserver.WebServer;


// Wont need any more
//import ros.*;
//import ros.communication.*;
//import ros.pkg.ros_simulink.srv.MatlabEval;

// Example shutdown hook class
class MyShutdown extends Thread {
    public void run() {
        System.out.println("MyShutdown hook called");
    }
}


public class rosmatlab
{
  private static final int port = 14441;

  public static void main(String[] args) throws Exception
  {
		WebServer webServer = new WebServer(port);
        
       	XmlRpcServer xmlRpcServer = webServer.getXmlRpcServer();
        
        PropertyHandlerMapping phm = new PropertyHandlerMapping();
		matlabinterface matlab = new matlabinterface();
		phm.setVoidMethodEnabled(true);
		phm.setRequestProcessorFactoryFactory(new MatlabRequestProcessorFactoryFactory(matlab));
		phm.addHandler("matlab", matlabinterface.class);
		xmlRpcServer.setHandlerMapping(phm);
	        
		XmlRpcServerConfigImpl serverConfig = (XmlRpcServerConfigImpl) xmlRpcServer.getConfig();
        serverConfig.setEnabledForExtensions(true);
        serverConfig.setContentLengthOptional(false);

        webServer.start();
	
/*	MyShutdown sh = new MyShutdown();
	Runtime.getRuntime().addShutdownHook(sh); 
	Ros ros = Ros.getInstance();
	ros.init("rosmatlab");
	NodeHandle n = ros.createNodeHandle();
	ros.logInfo("Starting Matlab/Simulink session");

    //Create a factory
    RemoteMatlabProxyFactory factory = new RemoteMatlabProxyFactory();

    //Get a proxy, launching MATLAB in the process
    final RemoteMatlabProxy proxy = factory.getProxy();

	ServiceServer.Callback<MatlabEval.Request,MatlabEval.Response> scb = 
       new ServiceServer.Callback<MatlabEval.Request,MatlabEval.Response>() {
            public MatlabEval.Response call(MatlabEval.Request request) {
                 MatlabEval.Response res = new MatlabEval.Response();
				 String evalstr = request.str;
			     
                 return res;
            }
       };
	try
	{                
    	ServiceServer<MatlabEval.Request,MatlabEval.Response,MatlabEval> srv = 
   	    n.advertiseService("eval", new MatlabEval(), scb);
	}
	catch(ros.RosException exp)
	{
	}
  
	ros.spin();
*/

  }
}
