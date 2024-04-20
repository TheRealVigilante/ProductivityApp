import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.*;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;

public class WebsiteList {

    private String name;
    private ArrayList<String> websites;
    private ArrayList<String> applications;

    public WebsiteList(String name) {
        this.name = name;
        this.websites = new ArrayList<>();
        this.applications = new ArrayList<>();
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public ArrayList<String> getWebsites() {
        return websites;
    }

    public void addWebsite(String website) {
        this.websites.add(website);
    }
}

class BlacklistGUI extends JFrame {
    private JTextArea websitesTextArea;
    private JButton submitButton;
    private final Object lock = new Object();
    private static HashMap<String, WebsiteList> websiteLists = new HashMap<>();
    private String currentListName;
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

    private void createBlacklist() {
        setTitle("Website Blacklist");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(300, 200);
        setLayout(new BorderLayout());

        websitesTextArea = new JTextArea(10, 20);
        JScrollPane scrollPane = new JScrollPane(websitesTextArea);
        add(scrollPane, BorderLayout.CENTER);

        submitButton = new JButton("Submit");
        submitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String[] websitesArray = websitesTextArea.getText().split("\n");
                ArrayList<String> websitesList = new ArrayList<>();
                for (String website : websitesArray) {
                    websitesList.add(website.trim());
                }
                synchronized (lock) {
                    lock.notify(); // Notify the waiting thread
                }
                // Notify the caller that the list is ready
                onWebsitesListReady(websitesList);
                dispose();
            }
        });
        add(submitButton, BorderLayout.SOUTH);
    }

    private void onWebsitesListReady(ArrayList<String> list) {
        // Process the websitesList here or notify the caller
        System.out.println("Blacklist: " + list);
        WebsiteList websiteList = new WebsiteList(currentListName);
        for (String website : list) {
            websiteList.addWebsite(website);
        }
        websiteLists.put(currentListName, websiteList);
    }
    public static void lockWebsites(String listName) {
        WebsiteList websiteList = websiteLists.get(listName);
        if (websiteList != null) {
            for (String website : websiteList.getWebsites()) {
                website = format(website);
                System.out.println("Locking: " + website);
                blockWebsite(website);
            }
        }
    }
    public void waitForSubmit() {
        synchronized (lock) {
            try {
                lock.wait(); // Wait until the button is clicked
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
    public static void unlockWebsites(String listName) throws IOException {
        WebsiteList websiteList = websiteLists.get(listName);
        if (websiteList != null) {
            for (String website : websiteList.getWebsites()) {
                System.out.println("Unlocking: " + website);
                unblockWebsite(website);
            }
        }
    }
    public void launchGUI(String listName) {
        this.currentListName = listName;
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                createBlacklist();
                setVisible(true);
            }
        });
    }
}
