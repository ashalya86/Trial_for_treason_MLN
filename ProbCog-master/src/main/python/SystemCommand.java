import java.io.*;
import java.util.*;

public class SystemCommand {

    public static void main(String args[]) throws IOException {

        // String command = "cmd /c dir";
        // String command1 = "cmd /c cd ..\\..";
        // Process p = Runtime.getRuntime().exec(command1);
        String command = "cmd /c python C:\\ProbCog-master\\src\\main\\python\\trialInfer.py";
        // String command = "cmd /c python C:\\PY4J\\CommandSystem\\src\\Hello.py";

        // String command = "cmd /c python
        // C:\\ProbCog-master\\src\\main\\python\\trialInfer.py";
        Process q = Runtime.getRuntime().exec(command);

        try (Scanner sc = new Scanner(q.getInputStream())) {

            System.out.printf("Output of the command: %s %n%n", command);
            while (sc.hasNext()) {
                System.out.println(sc.nextLine());
            }
        }
    }
}