
import matlabcontrol.*;

public class matlabinterface
{
    RemoteMatlabProxyFactory factory ;
    RemoteMatlabProxy proxy;
   	public matlabinterface() throws Exception
	{
		//Create a factory
		factory = new RemoteMatlabProxyFactory();
		//Get a proxy, launching MATLAB in the process
		proxy = factory.getProxy();
	}

	public void eval(String s) 
	{
		try
		{                 
			proxy.eval(s); 
		}
		catch(matlabcontrol.MatlabInvocationException ex)
		{
			
		}
	}	
}


