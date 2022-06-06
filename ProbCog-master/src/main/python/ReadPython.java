import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.ProcessBuilder.Redirect;
import java.io.File;
import java.io.FileInputStream;

public class ReadPython {
    public static void main(String[] args) throws IOException, InterruptedException {
        //String path = "C:\\Py4j\\CommandSystem\\src/Hello.py";
        // String path = "C:\\ProbCog-master\\src\\main\\python/Hello.py";
        String path = "C:\\ProbCog-master\\src\\main\\python/trialInfer.py";

        // ProcessBuilder pb = new ProcessBuilder("python",
        // "C:\\Py4j\\CommandSystem\\src/Hello.py").inheritIO();
        ProcessBuilder pb = new ProcessBuilder("python", path).inheritIO();
        File log = new File("log");
        pb.redirectErrorStream(true);
        pb.redirectOutput(Redirect.appendTo(log));

        Process p = pb.start();
        p.waitFor();

        assert pb.redirectInput() == Redirect.PIPE;
        assert pb.redirectOutput().file() == log;
        assert p.getInputStream().read() == -1;

        FileInputStream fstream = new FileInputStream("log");
        BufferedReader br = new BufferedReader(new InputStreamReader(fstream));
        String strLine;
        while ((strLine = br.readLine()) != null) {
            /* parse strLine to obtain what you want */
            System.out.println(strLine);
        }
        fstream.close();
    }
}