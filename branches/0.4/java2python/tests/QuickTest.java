final class QuickTest extends Object {
    class X {
	int y = 1;
    }

    int i;
    int j = 2;
    static int k;
    static int m = 3;

    public QuickTest(int z) {
	System.out.println("quick test ctor");
    }


    public String foo(int... bar) {
//	System.out.println("foo: " + bar);
	return "placeholder";
    }

    public static void main(String[] args) {
        System.out.println("Hello, world.");
	QuickTest q = new QuickTest(7);
	q.foo(4, 5, 6);
    }
}
