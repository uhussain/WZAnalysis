#ifndef WZSelector_h
#define WZSelector_h

#include <vector>
#include "Analysis/WZAnalysis/interface/WZSelectorBase.h"
#include <TH3.h>

class WZSelector : public WZSelectorBase {
public :
    bool doSystematics_;

    std::vector<std::string> systHists_ = {
        "yield",
        "backgroundControlYield",
        "mjj",
        "dEtajj",
        "MTWZ"
    };

    //std::vector<std::string> jeSystematicNames_ = {
    std::vector<std::string> systematicNames_ = {
        "jesUp", "jesDown", "jerUp", "jerDown"
    };

    //std::vector<std::string> systematicNames_ = {
    //    "mEffUp", "mEffDown", "eEffUp", "eEffDown",
    //    "pileupUp", "pileupDown"
    //};

    std::map<std::string, TH1D*> hists1D_ = {
        { "yield",  {} },
        { "backgroundControlYield",  {} },
        { "nTruePU",  {} },
        { "nvtx",  {} },
        { "ZMass",  {} },
        { "ZPt",  {} },
        { "ZEta",  {} },
        { "ZPhi",  {} },
        { "dR_lW_Z",  {} },
        { "Zlep1_Eta",  {} },
        { "Zlep1_Phi",  {} },
        { "Zlep1_Pt",  {} },
        { "Zlep2_Eta",  {} },
        { "Zlep2_Phi",  {} },
        { "Zlep2_Pt",  {} },
        { "Wlep_Eta",  {} },
        { "Wlep_Pt",  {} },
        { "Wlep_Phi",  {} },
        { "MET", {} },
        { "MTWZ", {} },
        { "M3lMET", {} },
        { "Mass", {} },
        { "Pt", {} },
        { "nJets", {} },
        { "nJetCSVv2T", {} },
        { "jetPt[0]", {} },
        { "jetPt[1]", {} },
        { "jetPt[2]", {} },
        { "jetEta12", {} },
        { "jetEta[0]", {} },
        { "jetEta[1]", {} },
        { "jetEta[2]", {} },
        { "mjj",  {} },
        { "MtW",  {} },
        { "dEtajj",  {} },
        { "zep3l",  {} },
        { "zepj3",  {} }
    };

    // Weight hists must be subset of 1D hists!
    std::map<std::string, TH2D*> weighthists_ = {
        { "backgroundControlYield",  {} },
        { "MTWZ",  {} },
        { "M3lMET", {} },
        { "yield",  {} }
    };
    
    std::map<std::string, TH2D*> hists2D_ = {
        {"mjj_etajj_2D", {}},
        {"mjj_dRjj_2D", {}}
    };

    std::vector<std::string> systHists2D_ = {
        "mjj_etajj_2D", "mjj_dRjj_2D"
    };

    std::map<std::string, TH3D*> weighthists2D_ {
        {"mjj_etajj_2D", {}},
        {"mjj_dRjj_2D", {}}
    };

    std::vector<float>* scaleWeights = NULL;
    std::vector<float>* pdfWeights = NULL;
    std::vector<float> lheWeights;
    unsigned int weight_info_;
    float dEtajj;
    float dEtajj_jesUp;
    float dEtajj_jesDown;
    float dEtajj_jerUp;
    float dEtajj_jerDown;
    float dRjj;
    float dRjj_jesUp;
    float dRjj_jesDown;
    float dRjj_jerUp;
    float dRjj_jerDown;
    float zep3l;
    float zep3l_jesUp;
    float zep3l_jesDown;
    float zep3l_jerUp;
    float zep3l_jerDown;
    std::vector<float>* jetEta = NULL;
    std::vector<float>* jetEta_jesUp = NULL;
    std::vector<float>* jetEta_jesDown = NULL;
    std::vector<float>* jetEta_jerUp = NULL;
    std::vector<float>* jetEta_jerDown = NULL;
    std::vector<float>* jetPhi = NULL;
    std::vector<float>* jetPhi_jesUp = NULL;
    std::vector<float>* jetPhi_jesDown = NULL;
    std::vector<float>* jetPhi_jerUp = NULL;
    std::vector<float>* jetPhi_jerDown = NULL;
    std::vector<float>* jetPt = NULL;
    std::vector<float>* jetPt_jesUp = NULL;
    std::vector<float>* jetPt_jesDown = NULL;
    std::vector<float>* jetPt_jerUp = NULL;
    std::vector<float>* jetPt_jerDown = NULL;
    std::vector<float>* jetCSVv2 = NULL;
    UInt_t nvtx;
    Float_t Mass;
    Float_t Eta;
    Float_t Pt;
    Float_t ZPt;
    Float_t ZEta;
    Float_t ZPhi;
    Float_t mjj;
    Float_t mjj_jesUp;
    Float_t mjj_jesDown;
    Float_t mjj_jerUp;
    Float_t mjj_jerDown;
    Float_t l1Phi;
    Float_t l2Phi;
    Float_t l3Phi;
    Float_t MtToMET;
    
    TBranch* b_l3MtToMET;
    TBranch* b_MtToMET;
    TBranch* b_pdfWeights;
    TBranch* b_scaleWeights;
    TBranch* b_jetCSVv2;
    TBranch* b_jetPt;
    TBranch* b_jetEta;
    TBranch* b_jetEta_jesUp;
    TBranch* b_jetEta_jesDown;
    TBranch* b_jetEta_jerUp;
    TBranch* b_jetEta_jerDown;
    TBranch* b_jetPhi;
    TBranch* b_jetPhi_jesUp;
    TBranch* b_jetPhi_jesDown;
    TBranch* b_jetPhi_jerUp;
    TBranch* b_jetPhi_jerDown;
    TBranch* b_jetPt_jesUp;
    TBranch* b_jetPt_jesDown;
    TBranch* b_jetPt_jerUp;
    TBranch* b_jetPt_jerDown;
    TBranch* b_nvtx;
    TBranch* b_Mass;
    TBranch* b_Eta;
    TBranch* b_Pt;
    TBranch* b_ZPt;
    TBranch* b_ZPhi;
    TBranch* b_ZEta;
    TBranch* b_mjj;
    TBranch* b_mjj_jesUp;
    TBranch* b_mjj_jesDown;
    TBranch* b_mjj_jerUp;
    TBranch* b_mjj_jerDown;
    TBranch* b_l1Phi;
    TBranch* b_l2Phi;
    TBranch* b_l3Phi;

    // Readers to access the data (delete the ones you do not need).
    WZSelector(TTree * /*tree*/ =0) { }
    virtual ~WZSelector() { }
    virtual void    Init(TTree *tree) override;
    virtual Bool_t  Process(Long64_t entry) override;
    virtual void    SetupNewDirectory() override;

    ClassDefOverride(WZSelector,0);
protected:
    void LoadBranches(Long64_t entry);
    void FillHistograms(Long64_t entry, float weight, bool noBlind);
    void FillVBSHistograms(Long64_t entry, float weight, bool noBlind);
    void FillVBSBackgroundControlHistograms(float weight, bool noBlind);
    bool PassesBaseSelection(bool tightLeps, Selection selection);
    bool PassesVBSSelection(bool noBlind, float dijetMass, 
            std::vector<float>* jPt, std::vector<float>* jEta);
    bool PassesVBSBackgroundControlSelection(float dijetMass, 
            std::vector<float>* jPt, std::vector<float>* jEta);
    void InitialzeHistogram(std::string name, std::vector<std::string> histData);
    unsigned int GetLheWeightInfo();
    std::vector<std::string> ReadHistData(std::string histDataString);
    template<typename T, typename... Args>
    void SafeHistFill(std::map<std::string, T*> container, 
            std::string histname, Args... args) {
        if (container[histname] != nullptr)
            container[histname]->Fill(args...);
    };
};

#endif

