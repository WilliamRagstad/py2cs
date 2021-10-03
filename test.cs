using System;
public class Program
{
	public static void Main(string[] args)
	{
		if (1 == 1)
		{
			Console.WriteLine("This is a test");
		}
		int a = 1;
		int b = 2;
		int c = 3;
		Console.WriteLine(a + b + c);
		bool d = 2 > 5;
		if (d)
		{
			Console.WriteLine("True");
		}
		else
		{
			Console.WriteLine("False");
		}
		int myFunc = (int x) => x + 1;
		Console.WriteLine(myFunc(1));
	}
}
