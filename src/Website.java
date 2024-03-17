
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayDeque;

public class Website {
    private static String hostsPath = "C:\\Windows\\System32\\drivers\\etc\\hosts";
//    private static String hostsPath="fakehost.txt";
    public static String format(String website){//www.youtube.com or https://youtube.com or https://www.youtube.com
        String http="https://";
        String www="www.";
        if (website.contains(http)){
            website=website.substring(8);
        }
        if (!website.contains(www)) {
            website=www+website;
        }
        return website;
    }
    public static void blockWebsite(String website) {
        String redirectIP = "127.0.0.1";
        try (FileWriter fw = new FileWriter(hostsPath, true);
             PrintWriter writer = new PrintWriter(fw)) {

            writer.println("\n" + redirectIP + " " + website);

        } catch (IOException e) {
            System.out.println("Error writing to the hosts file: " + e.getMessage());
        }
    }

    public static void unblockWebsite(String URL) throws IOException {
        BufferedReader reader=new BufferedReader(new FileReader(hostsPath));
        String line="";
        ArrayDeque<String> lines=new ArrayDeque<>();
        while((line=reader.readLine())!=null){
            if (!line.contains(URL))
                lines.addFirst(line);
        }
        reader.close();
        FileWriter f=new FileWriter(hostsPath,false);
        PrintWriter writer=new PrintWriter(f);
        while (!lines.isEmpty())
            writer.println(lines.removeLast());
        writer.close();
    }
}